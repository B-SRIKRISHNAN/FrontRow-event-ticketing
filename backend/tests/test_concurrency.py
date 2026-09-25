import asyncio
import uuid
import pytest
from sqlalchemy import text
from tests.test_holds import get_jwt_headers


@pytest.mark.asyncio
async def test_concurrency_collision_exact_one_winner(async_client, db_session):
    # Reset seat 5 to AVAILABLE state
    await db_session.execute(text("UPDATE seats SET status = 'AVAILABLE', current_hold_id = NULL WHERE id = 5"))
    await db_session.commit()

    # Generate 15 distinct authenticated users and headers
    concurrent_users_count = 15
    headers_list = []
    for i in range(concurrent_users_count):
        user_email = f"collision_user_{i}_{uuid.uuid4().hex[:6]}@frontrow.com"
        headers = await get_jwt_headers(async_client, email=user_email)
        headers_list.append(headers)

    # Clear dependency override so concurrent requests use real connection pool from app.db.session
    from app.main import app
    app.dependency_overrides.clear()

    # Launch 15 simultaneous hold requests targeting seat 5 at the exact same millisecond
    tasks = [
        async_client.post(
            "/api/v1/events/1/holds",
            headers=hdr,
            json={"seat_ids": [5]},
        )
        for hdr in headers_list
    ]

    responses = await asyncio.gather(*tasks)

    status_codes = [r.status_code for r in responses]
    successes = [r for r in responses if r.status_code == 201]
    conflicts = [r for r in responses if r.status_code == 409]

    print(f"\n[CONCURRENCY COLLISION TEST] 15 simultaneous requests results: {status_codes}")
    print(f"Successes (201): {len(successes)}, Conflicts (409): {len(conflicts)}")

    # CONSTITUTION PRINCIPLE V ASSERTIONS:
    # Exactly 1 request MUST succeed with HTTP 201 Created
    assert len(successes) == 1, f"Expected exactly 1 successful hold acquisition, got {len(successes)}"
    
    # All N - 1 remaining requests MUST return HTTP 409 Conflict
    assert len(conflicts) == concurrent_users_count - 1, f"Expected {concurrent_users_count - 1} conflicts, got {len(conflicts)}"

    # Verify winning hold matches seat 5 state in DB
    winning_hold_id = uuid.UUID(successes[0].json()["hold_id"])
    seat_res = await db_session.execute(text("SELECT status, current_hold_id FROM seats WHERE id = 5"))
    seat_status, current_hold_id = seat_res.fetchone()

    assert seat_status == "LOCKED"
    assert current_hold_id == winning_hold_id

    # Clean up test seat 5
    await db_session.execute(text("UPDATE seats SET status = 'AVAILABLE', current_hold_id = NULL WHERE id = 5"))
    await db_session.execute(text("DELETE FROM holds WHERE id = :id"), {"id": winning_hold_id})
    await db_session.commit()
