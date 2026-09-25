import pytest
from app.services.seat_matcher import SeatMatcher


@pytest.mark.asyncio
async def test_seat_matcher_contiguous_in_same_row(async_client, db_session):
    # Search for 2 adjacent seats in Event 1
    seat_ids, fallback = await SeatMatcher.match_candidate_seats(
        db=db_session,
        event_id=1,
        quantity=2,
        adjacency=True,
    )

    assert fallback is False
    assert len(seat_ids) == 2


@pytest.mark.asyncio
async def test_ai_search_endpoint_with_fallback(async_client):
    payload = {"query": "3 tickets together under $200"}
    response = await async_client.post("/api/v1/events/1/ai-search", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "quantity" in data
    assert "adjacency" in data
    assert "recommended_seat_ids" in data
    assert "fallback_to_manual" in data
