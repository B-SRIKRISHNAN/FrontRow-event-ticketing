import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Auth Schemas
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Event & Seat Schemas
class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    venue_name: str
    show_time: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SeatResponse(BaseModel):
    id: int
    event_id: int
    row: str
    seat_number: int
    section: str
    price: Decimal
    status: str
    current_hold_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class SeatMapResponse(BaseModel):
    event_id: int
    seats: List[SeatResponse]


# Hold Schemas
class HoldCreateRequest(BaseModel):
    seat_ids: List[int] = Field(..., min_length=1, max_length=10, description="List of seat IDs to hold (1-10 seats)")


class HoldResponse(BaseModel):
    hold_id: uuid.UUID
    event_id: int
    seat_ids: List[int]
    status: str
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Checkout & Order Schemas
class CheckoutRequest(BaseModel):
    payment_token: str = Field("mock_token_ok", description="Mock payment reference token")


class TicketResponse(BaseModel):
    id: int
    order_id: int
    seat_id: int
    price_paid: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: Decimal
    created_at: datetime
    tickets: List[TicketResponse]

    model_config = ConfigDict(from_attributes=True)


# AI Search Schemas
class AISearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language seat preference query")


class AISearchResponse(BaseModel):
    quantity: int
    adjacency: bool
    max_price: Optional[Decimal] = None
    preferred_section: Optional[str] = None
    recommended_seat_ids: List[int]
