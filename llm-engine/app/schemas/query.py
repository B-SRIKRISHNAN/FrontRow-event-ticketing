from typing import Optional
from pydantic import BaseModel, Field


class ParseQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")


class SeatSearchQuery(BaseModel):
    quantity: int = Field(default=1, ge=1, description="Number of tickets requested")
    adjacency: bool = Field(default=False, description="True if seats must be adjacent/together")
    max_price: Optional[float] = Field(default=None, description="Maximum price per ticket")
    preferred_section: Optional[str] = Field(default=None, description="Preferred seating section or row prefix")
