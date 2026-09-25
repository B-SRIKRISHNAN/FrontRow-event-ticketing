from abc import ABC, abstractmethod
from app.schemas.query import SeatSearchQuery


class LLMProvider(ABC):
    """
    Abstract swappable LLM provider interface.
    Guarantees Principle II decoupling: microservice handles semantic parsing
    without direct database access or ORM models.
    """

    @abstractmethod
    async def parse_query(self, prompt: str) -> SeatSearchQuery:
        """
        Extract structured ticket search parameters from natural language text.
        """
        pass
