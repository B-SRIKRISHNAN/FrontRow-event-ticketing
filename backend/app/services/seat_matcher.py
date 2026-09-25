import logging
from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.domain import Seat

logger = logging.getLogger("backend.seat_matcher")


class SeatMatcher:
    """
    Deterministic Candidate Seat Matching Engine.
    Strictly enforces Constitution Principle IV contiguity rules:
      - Rows act as seating tiers.
      - Candidate seats ordered strictly by `ORDER BY row ASC, seat_number ASC`.
      - Contiguity is defined strictly as consecutive `seat_number` values within the exact same `row`.
      - Seats across different rows can NEVER be grouped as contiguous.
    """

    @staticmethod
    async def match_candidate_seats(
        db: AsyncSession,
        event_id: int,
        quantity: int = 1,
        adjacency: bool = False,
        max_price: Optional[float] = None,
        preferred_section: Optional[str] = None,
    ) -> Tuple[List[int], bool]:
        """
        Matches candidate available seat IDs.
        Returns: Tuple[List[seat_ids], fallback_to_manual: bool]
        """
        logger.info(
            f"[SEAT-MATCHER] Matching seats for event_id={event_id} | "
            f"qty={quantity}, adjacency={adjacency}, max_price={max_price}, preferred_section='{preferred_section}'"
        )

        # Base query for AVAILABLE seats in event ordered strictly by row ASC, seat_number ASC
        query = (
            select(Seat)
            .where(Seat.event_id == event_id, Seat.status == "AVAILABLE")
            .order_by(Seat.row.asc(), Seat.seat_number.asc())
        )

        if max_price is not None:
            query = query.where(Seat.price <= max_price)

        if preferred_section is not None:
            section_clean = preferred_section.strip().upper()
            # Support section or row prefix matching
            query = query.where(
                (Seat.section.ilike(f"%{section_clean}%")) | (Seat.row.ilike(f"%{section_clean}%"))
            )

        result = await db.execute(query)
        seats = result.scalars().all()

        if not seats:
            logger.warning(
                f"[SEAT-MATCHER] 0 matching available seats found for event_id={event_id} with given criteria. "
                "Triggering manual fallback."
            )
            return [], True

        logger.info(
            f"[SEAT-MATCHER] Found {len(seats)} available matching seat(s) in DB: "
            f"{[{'id': s.id, 'row': s.row, 'num': s.seat_number, 'price': float(s.price), 'sec': s.section} for s in seats]}"
        )

        # Group available seats by row
        seats_by_row: dict[str, List[Seat]] = {}
        for s in seats:
            seats_by_row.setdefault(s.row, []).append(s)

        # Helper: Find first contiguous block of size `quantity` in a single row
        def find_contiguous_in_row(row_seats: List[Seat], size: int) -> Optional[List[int]]:
            if len(row_seats) < size:
                return None
            for i in range(len(row_seats) - size + 1):
                window = row_seats[i : i + size]
                is_contiguous = True
                for j in range(len(window) - 1):
                    if window[j + 1].seat_number != window[j].seat_number + 1:
                        is_contiguous = False
                        break
                if is_contiguous:
                    return [s.id for s in window]
            return None

        # Case 1: Adjacency is required (adjacency == True)
        if adjacency:
            for row_name, row_seat_list in seats_by_row.items():
                match = find_contiguous_in_row(row_seat_list, quantity)
                if match:
                    logger.info(f"[SEAT-MATCHER] Matched {quantity} contiguous seat(s) in Row '{row_name}': {match}")
                    return match, False
            logger.warning(
                f"[SEAT-MATCHER] Required adjacency={adjacency} for qty={quantity} could not be satisfied in any single row. "
                "Triggering manual fallback."
            )
            return [], True

        # Case 2: Adjacency is false/unset -> Prefer contiguous block in one row, fallback to non-contiguous
        for row_name, row_seat_list in seats_by_row.items():
            match = find_contiguous_in_row(row_seat_list, quantity)
            if match:
                logger.info(f"[SEAT-MATCHER] Matched {quantity} seat(s) in Row '{row_name}': {match}")
                return match, False

        # Non-contiguous fallback: Select first `quantity` seats in row ASC, seat_number ASC order
        non_contiguous_ids = [s.id for s in seats[:quantity]]
        if len(non_contiguous_ids) < quantity:
            logger.warning(
                f"[SEAT-MATCHER] Only found {len(non_contiguous_ids)} seat(s) of requested qty={quantity}. "
                "Triggering manual fallback."
            )
            return non_contiguous_ids, True

        logger.info(f"[SEAT-MATCHER] Selected non-adjacent candidate seat IDs: {non_contiguous_ids}")
        return non_contiguous_ids, False


seat_matcher = SeatMatcher()
