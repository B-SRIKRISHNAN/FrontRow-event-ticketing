import uuid
import pytest
from sqlalchemy import text


async def get_jwt_headers(async_client, email="holduser@frontrow.com", password="Password123!"):
    await async_client.post("/api/v1/auth/register", json={"email": email, "password": password})
    res = await async_client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_acquire_hold_and_release(async_client, db_session):
    # Reset seat state for test reliability
    await db_session.execute(text("UPDATE seats SET status = 'AVAILABLE', current_hold_id = NULL WHERE id IN (2, 3)"))
    await db_session.commit()

    headers = await get_jwt_headers(async_client, email="holdtest1@frontrow.com")

    # 1. Acquire hold for seat 2
    hold_res = await async_client.post(
        "/api/v1/events/1/holds",
        headers=headers,
        json={"seat_ids": [2]},
    )
    assert hold_res.status_code == 201
    hold_data = hold_res.json()
    assert hold_data["event_id"] == 1
    assert hold_data["seat_ids"] == [2]
    assert hold_data["status"] == "ACTIVE"
    hold_id = hold_data["hold_id"]

    # 2. Attempting to hold seat 2 again should return 409 Conflict
    headers2 = await get_jwt_headers(async_client, email="holdtest2@frontrow.com")
    dup_res = await async_client.post(
        "/api/v1/events/1/holds",
        headers=headers2,
        json={"seat_ids": [2]},
    )
    assert dup_res.status_code == 409

    # 3. Non-owner release should fail with 403 Forbidden
    forb_res = await async_client.delete(f"/api/v1/holds/{hold_id}", headers=headers2)
    assert forb_res.status_code == 403

    # 4. Owner release hold
    rel_res = await async_client.delete(f"/api/v1/holds/{hold_id}", headers=headers)
    assert rel_res.status_code == 200

    # 5. Verify seat 2 returns to AVAILABLE
    seat_res = await async_client.get("/api/v1/events/1/seats")
    seats = seat_res.json()["seats"]
    seat2 = next(s for s in seats if s["id"] == 2)
    assert seat2["status"] == "AVAILABLE"
