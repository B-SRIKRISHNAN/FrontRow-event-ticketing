import pytest
import httpx
from app.services.llm_client import LLMClient, ParsedSeatQuery


@pytest.mark.asyncio
async def test_llm_client_fallback_on_unreachable_server():
    # Points to non-existent server to test fallback handling
    client = LLMClient(base_url="http://localhost:59999", timeout=0.5)
    parsed, fallback = await client.parse_query("Find 2 seats together")

    assert fallback is True
    assert isinstance(parsed, ParsedSeatQuery)
    assert parsed.quantity == 2
    assert parsed.adjacency is True
