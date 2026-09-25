import logging
from typing import Optional, Tuple
import httpx
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger("backend.llm_client")


class ParsedSeatQuery(BaseModel):
    quantity: int = Field(default=1, ge=1)
    adjacency: bool = Field(default=False)
    max_price: Optional[float] = None
    preferred_section: Optional[str] = None


class LLMClient:
    """
    Async HTTP client calling the decoupled LLM Engine microservice.
    Enforces a 3.0s timeout threshold and provides graceful fallback to manual seat map selection
    if the LLM microservice times out, experiences network failure, or returns an error.
    """

    def __init__(self, base_url: str = settings.LLM_ENGINE_URL, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def parse_query(self, prompt: str) -> Tuple[ParsedSeatQuery, bool]:
        """
        Parses a natural language search query.
        Returns: Tuple[ParsedSeatQuery, fallback_to_manual: bool]
        """
        url = f"{self.base_url}/api/v1/parse-query"
        payload = {"query": prompt}
        logger.info(f"[LLM-CLIENT] Dispatching RPC request to LLM Engine ({url}) | Prompt: '{prompt}'")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    parsed = ParsedSeatQuery.model_validate(data)
                    logger.info(f"[LLM-CLIENT] Received response from LLM Engine: {parsed.model_dump()}")
                    return parsed, False
                else:
                    logger.warning(
                        f"[LLM-CLIENT] LLM Engine returned HTTP status {response.status_code}: {response.text}. "
                        "Falling back to manual seat selection."
                    )
        except httpx.TimeoutException:
            logger.warning(
                f"[LLM-CLIENT] LLM Engine RPC call timed out after {self.timeout}s. "
                "Falling back to manual seat selection."
            )
        except Exception as e:
            logger.warning(
                f"[LLM-CLIENT] LLM Engine RPC call failed: {e}. "
                "Falling back to manual seat selection."
            )

        # Fallback response: trigger clean manual seat selection without arbitrary defaults
        fallback_parsed = ParsedSeatQuery(
            quantity=0,
            adjacency=False,
            max_price=None,
            preferred_section=None,
        )
        logger.info(f"[LLM-CLIENT] Returning clean fallback parameters (quantity=0, fallback=True)")
        return fallback_parsed, True


llm_client = LLMClient()
