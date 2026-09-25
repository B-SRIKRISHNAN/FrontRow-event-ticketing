import logging
from app.providers.base import LLMProvider
from app.providers.mock import MockProvider
from app.schemas.query import SeatSearchQuery

logger = logging.getLogger("llm_engine.gemini")


class GeminiProvider(LLMProvider):
    """
    Google Gemini provider using official google-genai SDK.
    Utilizes structured JSON output mode to extract Pydantic SeatSearchQuery objects.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.mock_fallback = MockProvider()
        self.client = None

        if api_key and api_key != "your_gemini_api_key_here":
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai client: {e}. Will fall back to mock provider.")

    async def parse_query(self, prompt: str) -> SeatSearchQuery:
        if not self.client:
            logger.info("Gemini API key missing or uninitialized. Falling back to MockProvider.")
            return await self.mock_fallback.parse_query(prompt)

        system_instruction = (
            "You are an expert ticket query parser for FrontRow event ticketing.\n"
            "Extract structured search parameters from the user's natural language input into JSON matching the schema:\n"
            "- quantity: integer, number of tickets (default 1)\n"
            "- adjacency: boolean, true if seats should be together/adjacent (default false)\n"
            "- max_price: float or null, maximum price per ticket\n"
            "- preferred_section: string or null, preferred seating section or row\n"
            "Return valid JSON only."
        )

        full_prompt = f"{system_instruction}\n\nUser Query: {prompt}"
        logger.info(f"[GEMINI-PROVIDER] Calling Gemini model '{self.model_name}' with prompt: '{prompt}'")

        try:
            # Call Gemini structured output mode
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": SeatSearchQuery,
                },
            )

            if response and response.text:
                logger.info(f"[GEMINI-PROVIDER] Gemini Raw Output: '{response.text.strip()}'")
                parsed = SeatSearchQuery.model_validate_json(response.text)
                logger.info(f"[GEMINI-PROVIDER] Parsed SeatSearchQuery: {parsed.model_dump()}")
                return parsed

        except Exception as e:
            logger.error(f"[GEMINI-PROVIDER] Gemini API call failed: {e}. Falling back to MockProvider.")

        return await self.mock_fallback.parse_query(prompt)
