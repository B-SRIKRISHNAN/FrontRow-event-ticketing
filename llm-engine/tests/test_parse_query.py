import pytest
from app.providers.mock import MockProvider
from app.schemas.query import SeatSearchQuery


@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "llm-engine"


@pytest.mark.asyncio
async def test_mock_provider_parsing():
    provider = MockProvider()

    # Query 1: Quantity, adjacency, max_price, section
    query1 = await provider.parse_query("Find 2 seats together in Section A under $150")
    assert query1.quantity == 2
    assert query1.adjacency is True
    assert query1.max_price == 150.0
    assert query1.preferred_section == "A"

    # Query 2: Single ticket without budget
    query2 = await provider.parse_query("1 ticket front row")
    assert query2.quantity == 1
    assert query2.preferred_section == "A"

    # Query 3: Non-adjacent / budget
    query3 = await provider.parse_query("3 tickets under $50")
    assert query3.quantity == 3
    assert query3.max_price == 50.0


@pytest.mark.asyncio
async def test_parse_query_endpoint(async_client):
    payload = {"query": "2 seats together near Section B for under $100"}
    response = await async_client.post("/api/v1/parse-query", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["quantity"] == 2
    assert data["adjacency"] is True
    assert data["max_price"] == 100.0
    assert data["preferred_section"] == "B"


@pytest.mark.asyncio
async def test_parse_query_validation_error(async_client):
    # Empty payload missing 'query'
    response = await async_client.post("/api/v1/parse-query", json={})
    assert response.status_code == 422
