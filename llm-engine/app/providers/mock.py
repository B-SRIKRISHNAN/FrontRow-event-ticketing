import logging
import re
from app.providers.base import LLMProvider
from app.schemas.query import SeatSearchQuery

logger = logging.getLogger("llm_engine.mock")


class MockProvider(LLMProvider):
    """
    Offline/mock LLM provider utilizing heuristic regex & keyword extraction.
    Provides immediate response without external API calls or network dependencies.
    """

    async def parse_query(self, prompt: str) -> SeatSearchQuery:
        text = prompt.lower()
        logger.info(f"[MOCK-PROVIDER] Parsing natural language prompt: '{prompt}'")

        # Extract quantity
        quantity = 1
        num_match = re.search(r"(\d+)\s*(?:seats|tickets|place|people|persons)?", text)
        if num_match:
            try:
                parsed_qty = int(num_match.group(1))
                if 1 <= parsed_qty <= 10:
                    quantity = parsed_qty
            except ValueError:
                pass

        if "single" in text or "1 seat" in text or "one ticket" in text:
            quantity = 1
        elif "pair" in text or "couple" in text or "2 seats" in text or "two tickets" in text:
            quantity = 2
        elif "trio" in text or "3 seats" in text or "three tickets" in text:
            quantity = 3
        elif "4 seats" in text or "four tickets" in text:
            quantity = 4

        # Extract adjacency / contiguity preference
        adjacency = False
        if any(word in text for word in ["together", "adjacent", "next to", "consecutive", "side by side"]):
            adjacency = True

        # Extract max price
        max_price = None
        # Look for explicit dollar signs ($150, $50) or 'under 100' / 'less than 100'
        price_match = re.search(r"(?:\$|under\s*\$?|less than\s*\$?)\s*(\d+(?:\.\d{1,2})?)", text)
        if price_match:
            try:
                val = float(price_match.group(1))
                if val > 0:
                    max_price = val
            except ValueError:
                pass

        if max_price is None and any(word in text for word in ["under", "less than", "cheap", "budget"]):
            max_price = 150.0

        # Extract preferred section / tier
        preferred_section = None
        section_match = re.search(r"(?:section|sec|tier|row)\s*([a-z0-9]+)", text)
        if section_match:
            preferred_section = section_match.group(1).upper()
        elif "front" in text:
            preferred_section = "A"
        elif "middle" in text:
            preferred_section = "B"
        elif "balcony" in text or "back" in text:
            preferred_section = "C"

        result = SeatSearchQuery(
            quantity=quantity,
            adjacency=adjacency,
            max_price=max_price,
            preferred_section=preferred_section,
        )
        logger.info(
            f"[MOCK-PROVIDER] Extracted Params -> quantity={quantity}, adjacency={adjacency}, "
            f"max_price={max_price}, preferred_section={preferred_section}"
        )
        return result
