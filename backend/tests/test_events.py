import uuid
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_list_events(async_client):
    response = await async_client.get("/api/v1/events")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)
    assert len(events) >= 1
    assert events[0]["title"] == "FrontRow Grand Concert"


@pytest.mark.asyncio
async def test_get_event_seats_and_lazy_expiry(async_client, db_session):
    # 1. Fetch seat map for event 1
    response = await async_client.get("/api/v1/events/1/seats")
    assert response.status_code == 200
    seat_map = response.json()
    assert seat_map["event_id"] == 1
    assert len(seat_map["seats"]) == 30

    # 2. Insert an expired hold and lock seat 1 manually for testing lazy expiry
    hold_id = uuid.uuid4()
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    
    # Get user 1 ID
    user_res = await db_session.execute(text("SELECT id FROM users LIMIT 1"))
    user_id = user_res.scalar_one()

    await db_session.execute(
        text(
            """
            INSERT INTO holds (id, user_id, event_id, status, created_at, expires_at)
            VALUES (:id, :user_id, 1, 'ACTIVE', NOW() - INTERVAL '15 minutes', :expires_at)
            """
        ),
        {"id": hold_id, "user_id": user_id, "expires_at": expired_time},
    )
    await db_session.execute(
        text(
            """
            UPDATE seats SET status = 'LOCKED', current_hold_id = :hold_id WHERE id = 1
            """
        ),
        {"hold_id": hold_id},
    )
    await db_session.commit()

    # 3. Request seat map; seat 1 should project status = AVAILABLE due to lazy expiry
    response2 = await async_client.get("/api/v1/events/1/seats")
    assert response2.status_code == 200
    seats2 = response2.json()["seats"]
    seat1 = next(s for s in seats2 if s["id"] == 1)
    assert seat1["status"] == "AVAILABLE"
    assert seat1["current_hold_id"] is None

    # Clean up test hold and restore seat 1
    await db_session.execute(text("UPDATE seats SET status = 'AVAILABLE', current_hold_id = NULL WHERE id = 1"))
    await db_session.execute(text("DELETE FROM holds WHERE id = :id"), {"id": hold_id})
    await db_session.commit()
