from datetime import datetime, timezone
from decimal import Decimal
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
from app.services.llm_client import llm_client
from app.services.seat_matcher import seat_matcher

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

    # Call decoupled LLM Engine microservice (with 3.0s timeout & fallback)
    parsed_params, llm_fallback = await llm_client.parse_query(payload.query)

    # Execute deterministic row-as-tier contiguity seat matching (Principle IV)
    recommended_ids, matcher_fallback = await seat_matcher.match_candidate_seats(
        db=db,
        event_id=id,
        quantity=parsed_params.quantity,
        adjacency=parsed_params.adjacency,
        max_price=parsed_params.max_price,
        preferred_section=parsed_params.preferred_section,
    )

    fallback_to_manual = llm_fallback or matcher_fallback

    return AISearchResponse(
        quantity=parsed_params.quantity,
        adjacency=parsed_params.adjacency,
        max_price=Decimal(str(parsed_params.max_price)) if parsed_params.max_price else None,
        preferred_section=parsed_params.preferred_section,
        recommended_seat_ids=recommended_ids,
        fallback_to_manual=fallback_to_manual,
    )
