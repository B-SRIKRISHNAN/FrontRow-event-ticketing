import uuid
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import text
from app.workers.sweeper import sweep_expired_holds


@pytest.mark.asyncio
async def test_sweeper_worker_recycling(db_session):
    # Reset seat 4 state
    await db_session.execute(text("UPDATE seats SET status = 'AVAILABLE', current_hold_id = NULL WHERE id = 4"))
    await db_session.commit()

    # Get user 1 ID
    user_res = await db_session.execute(text("SELECT id FROM users LIMIT 1"))
    user_id = user_res.scalar_one()

    # Create an expired hold manually
    hold_id = uuid.uuid4()
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=10)

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
        text("UPDATE seats SET status = 'LOCKED', current_hold_id = :hold_id WHERE id = 4"),
        {"hold_id": hold_id},
    )
    await db_session.commit()

    # Execute single pass of sweeper worker
    cleaned_count = await sweep_expired_holds()
    assert cleaned_count >= 1

    # Verify seat 4 is recycled to AVAILABLE
    seat_res = await db_session.execute(text("SELECT status, current_hold_id FROM seats WHERE id = 4"))
    seat_status, current_hold_id = seat_res.fetchone()
    assert seat_status == "AVAILABLE"
    assert current_hold_id is None

    # Verify hold status is EXPIRED
    hold_res = await db_session.execute(text("SELECT status FROM holds WHERE id = :id"), {"id": hold_id})
    hold_status = hold_res.scalar_one()
    assert hold_status == "EXPIRED"


@pytest.mark.asyncio
async def test_ai_search_stub_endpoint(async_client):
    res = await async_client.post(
        "/api/v1/events/1/ai-search",
        json={"query": "I want 2 front row seats in Section A"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["quantity"] == 2
    assert data["adjacency"] is True
    assert data["preferred_section"] == "A"
    assert isinstance(data["recommended_seat_ids"], list)
