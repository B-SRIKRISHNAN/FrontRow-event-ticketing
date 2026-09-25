import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.payment import process_mock_payment, process_mock_refund
from app.db.session import get_db
from app.models.domain import User
from app.schemas.dto import CheckoutRequest, OrderResponse, TicketResponse

router = APIRouter()


@router.post("/holds/{hold_id}/checkout", response_model=OrderResponse)
@router.post("/checkout/holds/{hold_id}", response_model=OrderResponse)
async def checkout_hold(
    hold_id: uuid.UUID,
    payload: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Fetch hold
    hold_res = await db.execute(
        text("SELECT id, user_id, event_id, status, expires_at FROM holds WHERE id = :id"),
        {"id": hold_id},
    )
    hold = hold_res.fetchone()
    if not hold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hold with ID {hold_id} not found.",
        )

    h_id, h_user_id, h_event_id, h_status, h_expires_at = hold

    # Principle II: JWT Ownership check
    if h_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to checkout a hold belonging to another user.",
        )

    now = datetime.now(timezone.utc)
    if h_status != "ACTIVE" or (h_expires_at and h_expires_at < now):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Hold has expired or is no longer active for checkout.",
        )

    # Fetch associated seats
    seats_res = await db.execute(
        text("SELECT id, price, status FROM seats WHERE current_hold_id = :hold_id"),
        {"hold_id": hold_id},
    )
    seats = seats_res.fetchall()
    if not seats:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No seats associated with this hold.",
        )

    total_amount = sum((seat[1] for seat in seats), Decimal("0.00"))
    seat_ids = [seat[0] for seat in seats]

    # 1. Execute Mock Payment Stub
    try:
        pay_ref = process_mock_payment(total_amount, current_user.id, payload.payment_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # 2. Atomic Checkout DB Transaction
    try:
        # Conditional seat update to SOLD
        update_seats_sql = text(
            """
            UPDATE seats
            SET status = 'SOLD'
            WHERE current_hold_id = :hold_id
              AND status = 'LOCKED'
              AND id = ANY(:seat_ids)
            """
        )
        res = await db.execute(update_seats_sql, {"hold_id": hold_id, "seat_ids": seat_ids})
        updated_rows = res.rowcount

        # Re-check hold expiry inside transaction
        check_hold_sql = text("SELECT expires_at FROM holds WHERE id = :id AND status = 'ACTIVE'")
        chk_res = await db.execute(check_hold_sql, {"id": hold_id})
        curr_hold = chk_res.fetchone()

        if updated_rows != len(seat_ids) or not curr_hold or curr_hold[0] < datetime.now(timezone.utc):
            # Roll back atomic transaction
            await db.rollback()

            # Mark hold expired & issue mock refund
            await db.execute(text("UPDATE holds SET status = 'EXPIRED' WHERE id = :id"), {"id": hold_id})
            await db.commit()
            process_mock_refund(pay_ref, total_amount)

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hold expired or modified during payment processing. Payment refunded.",
            )

        # Create Order
        insert_order_sql = text(
            """
            INSERT INTO orders (user_id, total_amount, created_at)
            VALUES (:user_id, :total_amount, NOW())
            RETURNING id, created_at;
            """
        )
        order_res = await db.execute(
            insert_order_sql,
            {"user_id": current_user.id, "total_amount": total_amount},
        )
        order_id, order_created_at = order_res.fetchone()

        # Update Hold to COMPLETED and link order_id
        update_hold_sql = text(
            """
            UPDATE holds
            SET status = 'COMPLETED', order_id = :order_id
            WHERE id = :hold_id;
            """
        )
        await db.execute(update_hold_sql, {"hold_id": hold_id, "order_id": order_id})

        # Insert Tickets
        ticket_dtos: List[TicketResponse] = []
        for seat in seats:
            seat_id_val, price_val, _ = seat
            insert_ticket_sql = text(
                """
                INSERT INTO tickets (order_id, seat_id, price_paid, created_at)
                VALUES (:order_id, :seat_id, :price_paid, NOW())
                RETURNING id, created_at;
                """
            )
            t_res = await db.execute(
                insert_ticket_sql,
                {"order_id": order_id, "seat_id": seat_id_val, "price_paid": price_val},
            )
            ticket_id, ticket_created_at = t_res.fetchone()
            ticket_dtos.append(
                TicketResponse(
                    id=ticket_id,
                    order_id=order_id,
                    seat_id=seat_id_val,
                    price_paid=price_val,
                    created_at=ticket_created_at,
                )
            )

        await db.commit()

        return OrderResponse(
            id=order_id,
            user_id=current_user.id,
            total_amount=total_amount,
            created_at=order_created_at,
            tickets=ticket_dtos,
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        process_mock_refund(pay_ref, total_amount)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during checkout processing: {e}",
        )
