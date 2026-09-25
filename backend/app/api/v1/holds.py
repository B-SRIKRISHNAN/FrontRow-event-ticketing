import uuid
from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg.exceptions import LockNotAvailableError

from app.config import settings
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.domain import Event, User
from app.schemas.dto import HoldCreateRequest, HoldResponse

router = APIRouter()


@router.post("/events/{id}/holds", response_model=HoldResponse, status_code=status.HTTP_201_CREATED)
async def acquire_hold(
    id: int,
    payload: HoldCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    requested_seat_ids = payload.seat_ids
    if not requested_seat_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one seat ID must be specified for hold acquisition.",
        )

    # Principle I: Deterministic Acquisition (Sort seat IDs ascending to prevent circular deadlocks)
    sorted_seat_ids = sorted(list(set(requested_seat_ids)))

    # Verify event existence
    event_res = await db.execute(text("SELECT id FROM events WHERE id = :id"), {"id": id})
    if not event_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {id} not found.",
        )

    # Principle I: Concurrency-critical raw parameterized SQL with FOR UPDATE OF s NOWAIT
    # Principle I: LEFT JOIN from seats s to holds h on current_hold_id
    lock_query = text(
        """
        SELECT s.id, s.status, s.price, s.current_hold_id, h.expires_at
        FROM seats s
        LEFT JOIN holds h ON s.current_hold_id = h.id
        WHERE s.event_id = :event_id
          AND s.id = ANY(:seat_ids)
        ORDER BY s.id ASC
        FOR UPDATE OF s NOWAIT;
        """
    )
    try:
        res = await db.execute(lock_query, {"event_id": id, "seat_ids": sorted_seat_ids})
        locked_rows = res.fetchall()
    except Exception as e:
        await db.rollback()
        # Catch PostgreSQL error code 55P03 (lock_not_available)
        err_msg = str(e).lower()
        if "55p03" in err_msg or "could not obtain lock" in err_msg or isinstance(e, LockNotAvailableError):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="One or more requested seats are currently locked by a concurrent transaction.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to acquire seat lock due to concurrency contention.",
        )

    # Atomic Availability Predicate & Count Check
    now = datetime.now(timezone.utc)
    if len(locked_rows) != len(sorted_seat_ids):
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="One or more requested seat IDs do not exist for this event.",
        )

    for row in locked_rows:
        seat_id, status_val, price, current_hold_id, expires_at = row
        # Evaluate availability: AVAILABLE or (LOCKED and holds.expires_at < NOW())
        is_available = status_val == "AVAILABLE" or (
            status_val == "LOCKED" and expires_at is not None and expires_at < now
        )
        if not is_available:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Seat ID {seat_id} is unavailable or locked by an active hold.",
            )

    # Create Hold & Update Seats within the same transaction
    new_hold_id = uuid.uuid4()
    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(seconds=settings.HOLD_DURATION_SECONDS)

    # Insert Hold
    insert_hold_sql = text(
        """
        INSERT INTO holds (id, user_id, event_id, status, created_at, expires_at)
        VALUES (:id, :user_id, :event_id, 'ACTIVE', :created_at, :expires_at);
        """
    )
    await db.execute(
        insert_hold_sql,
        {
            "id": new_hold_id,
            "user_id": current_user.id,
            "event_id": id,
            "created_at": created_at,
            "expires_at": expires_at,
        },
    )

    # Update Seats to LOCKED with new_hold_id
    update_seats_sql = text(
        """
        UPDATE seats
        SET status = 'LOCKED', current_hold_id = :hold_id
        WHERE id = ANY(:seat_ids);
        """
    )
    await db.execute(update_seats_sql, {"hold_id": new_hold_id, "seat_ids": sorted_seat_ids})

    await db.commit()

    return HoldResponse(
        hold_id=new_hold_id,
        event_id=id,
        seat_ids=sorted_seat_ids,
        status="ACTIVE",
        created_at=created_at,
        expires_at=expires_at,
    )


@router.delete("/holds/{hold_id}")
async def release_hold(
    hold_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Fetch hold
    hold_res = await db.execute(text("SELECT id, user_id, status FROM holds WHERE id = :id"), {"id": hold_id})
    hold = hold_res.fetchone()

    if not hold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hold with ID {hold_id} not found.",
        )

    h_id, h_user_id, h_status = hold

    # Principle II: JWT Ownership check
    if h_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to release a hold belonging to another user.",
        )

    if h_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot release hold in '{h_status}' state.",
        )

    # Update hold status to EXPIRED & reset seats to AVAILABLE
    await db.execute(text("UPDATE holds SET status = 'EXPIRED' WHERE id = :id"), {"id": hold_id})
    await db.execute(
        text("UPDATE seats SET status = 'AVAILABLE', current_hold_id = NULL WHERE current_hold_id = :id"),
        {"id": hold_id},
    )
    await db.commit()

    return {"message": "Hold released successfully"}
