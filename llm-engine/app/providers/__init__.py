from app.config import settings
from app.providers.base import LLMProvider
from app.providers.gemini import GeminiProvider
from app.providers.mock import MockProvider


def get_llm_provider() -> LLMProvider:
    provider_name = settings.LLM_PROVIDER.lower()
    if provider_name == "gemini":
        return GeminiProvider(api_key=settings.GEMINI_API_KEY)
    else:
        return MockProvider()


__all__ = ["LLMProvider", "GeminiProvider", "MockProvider", "get_llm_provider"]
