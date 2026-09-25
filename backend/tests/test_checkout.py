import pytest
from sqlalchemy import text
from tests.test_holds import get_jwt_headers


@pytest.mark.asyncio
async def test_checkout_and_order_history(async_client, db_session):
    # Reset seat 3 state for clean test run
    await db_session.execute(text("UPDATE seats SET status = 'AVAILABLE', current_hold_id = NULL WHERE id = 3"))
    await db_session.commit()

    headers = await get_jwt_headers(async_client, email="checkoutuser@frontrow.com")

    # 1. Hold seat 3
    hold_res = await async_client.post(
        "/api/v1/events/1/holds",
        headers=headers,
        json={"seat_ids": [3]},
    )
    assert hold_res.status_code == 201
    hold_id = hold_res.json()["hold_id"]

    # 2. Checkout hold
    chk_res = await async_client.post(
        f"/api/v1/holds/{hold_id}/checkout",
        headers=headers,
        json={"payment_token": "mock_token_ok"},
    )
    assert chk_res.status_code == 200
    order_data = chk_res.json()
    assert order_data["id"] is not None
    assert len(order_data["tickets"]) == 1
    assert order_data["tickets"][0]["seat_id"] == 3

    # 3. Double checkout attempt should return 409 Conflict
    dup_chk = await async_client.post(
        f"/api/v1/holds/{hold_id}/checkout",
        headers=headers,
        json={"payment_token": "mock_token_ok"},
    )
    assert dup_chk.status_code == 409

    # 4. GET /orders should return the created order
    orders_res = await async_client.get("/api/v1/orders", headers=headers)
    assert orders_res.status_code == 200
    orders = orders_res.json()
    assert len(orders) >= 1
    assert orders[0]["id"] == order_data["id"]

    # Clean up test seat 3
    await db_session.execute(text("UPDATE seats SET status = 'AVAILABLE', current_hold_id = NULL WHERE id = 3"))
    await db_session.commit()
