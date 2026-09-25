from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.domain import Event, Hold, Seat
from app.schemas.dto import (
    AISearchRequest,
    AISearchResponse,
    EventResponse,
    SeatMapResponse,
    SeatResponse,
)

router = APIRouter()


@router.get("", response_model=List[EventResponse])
async def list_events(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).order_by(Event.id.asc()))
    events = result.scalars().all()
    return events


@router.get("/{id}/seats", response_model=SeatMapResponse)
async def get_event_seats(id: int, db: AsyncSession = Depends(get_db)):
    # Check event existence
    event_res = await db.execute(select(Event).where(Event.id == id))
    event = event_res.scalar_one_or_none()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {id} not found.",
        )

    # Fetch seats with hold relationship loaded
    seats_res = await db.execute(
        select(Seat)
        .options(selectinload(Seat.current_hold))
        .where(Seat.event_id == id)
        .order_by(Seat.row.asc(), Seat.seat_number.asc())
    )
    seats = seats_res.scalars().all()

    now = datetime.now(timezone.utc)
    seat_responses: List[SeatResponse] = []

    for seat in seats:
        effective_status = seat.status
        effective_hold_id = seat.current_hold_id

        # Tri-Layer Lease Lifecycle: Lazy Expiration on Read
        # If seat status is LOCKED but the associated hold has expired, project as AVAILABLE
        if seat.status == "LOCKED" and seat.current_hold:
            if seat.current_hold.expires_at and seat.current_hold.expires_at < now:
                effective_status = "AVAILABLE"
                effective_hold_id = None

        seat_dto = SeatResponse(
            id=seat.id,
            event_id=seat.event_id,
            row=seat.row,
            seat_number=seat.seat_number,
            section=seat.section,
            price=seat.price,
            status=effective_status,
            current_hold_id=effective_hold_id,
        )
        seat_responses.append(seat_dto)

    return SeatMapResponse(event_id=id, seats=seat_responses)


@router.post("/{id}/ai-search", response_model=AISearchResponse)
async def ai_search_seats(
    id: int,
    payload: AISearchRequest,
    db: AsyncSession = Depends(get_db),
):
    # Verify event existence
    event_res = await db.execute(select(Event).where(Event.id == id))
    if not event_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {id} not found.",
        )

    # AI search stub: returns candidate seat preferences based on query keyword hints
    query_text = payload.query.lower()

    quantity = 2
    if "1 seat" in query_text or "single" in query_text:
        quantity = 1
    elif "3 seats" in query_text:
        quantity = 3

    adjacency = True
    if "non-adjacent" in query_text or "separate" in query_text:
        adjacency = False

    preferred_section = None
    if "front" in query_text or "row a" in query_text:
        preferred_section = "A"

    # Select candidate available seat IDs
    seats_res = await db.execute(
        select(Seat.id)
        .where(Seat.event_id == id, Seat.status == "AVAILABLE")
        .order_by(Seat.row.asc(), Seat.seat_number.asc())
        .limit(quantity)
    )
    recommended_ids = list(seats_res.scalars().all())

    return AISearchResponse(
        quantity=quantity,
        adjacency=adjacency,
        max_price=150.00,
        preferred_section=preferred_section,
        recommended_seat_ids=recommended_ids,
    )
