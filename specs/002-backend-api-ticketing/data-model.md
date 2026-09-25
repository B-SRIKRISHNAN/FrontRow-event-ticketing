# Data Model & Domain Entity Specifications: Core Backend API (Ticketing)

**Feature**: `002-backend-api-ticketing` | **Date**: 2026-09-25

## 1. Domain Entities & Schema Definitions

```mermaid
erDiagram
    users ||--o{ holds : creates
    users ||--o{ orders : owns
    events ||--o{ seats : contains
    events ||--o{ holds : targets
    holds ||--o{ seats : locks
    orders ||--o{ tickets : includes
    seats ||--o{ tickets : produces
    holds |o--o| orders : completes_to

    users {
        bigint id PK
        string email UK
        string hashed_password
        timestamptz created_at
    }

    events {
        bigint id PK
        string title
        text description
        string venue_name
        timestamptz show_time
        timestamptz created_at
    }

    seats {
        bigint id PK
        bigint event_id FK
        string row
        int seat_number
        string section
        numeric price
        string status
        uuid current_hold_id FK
    }

    holds {
        uuid id PK
        bigint user_id FK
        bigint event_id FK
        string status
        timestamptz created_at
        timestamptz expires_at
        bigint order_id FK
    }

    orders {
        bigint id PK
        bigint user_id FK
        numeric total_amount
        timestamptz created_at
    }

    tickets {
        bigint id PK
        bigint order_id FK
        bigint seat_id FK
        numeric price_paid
        timestamptz created_at
    }
```

---

## 2. Pydantic Schemas (Request / Response DTOs)

### Authentication DTOs
- `UserRegisterRequest`: `email: EmailStr`, `password: str` (min length 8)
- `UserLoginRequest`: `email: EmailStr`, `password: str`
- `TokenResponse`: `access_token: str`, `token_type: str = "bearer"`
- `UserResponse`: `id: int`, `email: str`, `created_at: datetime`

### Event & Seat DTOs
- `EventResponse`: `id: int`, `title: str`, `description: str | None`, `venue_name: str`, `show_time: datetime`, `created_at: datetime`
- `SeatResponse`: `id: int`, `event_id: int`, `row: str`, `seat_number: int`, `section: str`, `price: Decimal`, `status: str`, `current_hold_id: UUID | None`
- `SeatMapResponse`: `event_id: int`, `seats: list[SeatResponse]`

### Hold DTOs
- `HoldCreateRequest`: `seat_ids: list[int]` (min items 1, max items 10)
- `HoldResponse`: `hold_id: UUID`, `event_id: int`, `seat_ids: list[int]`, `status: str`, `created_at: datetime`, `expires_at: datetime`

### Checkout & Order DTOs
- `CheckoutRequest`: `payment_token: str = "mock_token_ok"`
- `TicketResponse`: `id: int`, `order_id: int`, `seat_id: int`, `price_paid: Decimal`, `created_at: datetime`
- `OrderResponse`: `id: int`, `user_id: int`, `total_amount: Decimal`, `created_at: datetime`, `tickets: list[TicketResponse]`

### AI Search DTOs
- `AISearchRequest`: `query: str`
- `AISearchResponse`: `quantity: int`, `adjacency: bool`, `max_price: Decimal | None`, `preferred_section: str | None`, `recommended_seat_ids: list[int]`

---

## 3. State Transitions

### Seat Status State Machine
- `AVAILABLE` $\rightarrow$ `LOCKED` (on hold acquisition)
- `LOCKED` $\rightarrow$ `SOLD` (on successful checkout)
- `LOCKED` $\rightarrow$ `AVAILABLE` (on lease sweeper expiration or explicit hold release)

### Hold Status State Machine
- `ACTIVE` $\rightarrow$ `COMPLETED` (on successful checkout; links to `order_id`)
- `ACTIVE` $\rightarrow$ `EXPIRED` (on lease sweeper execution, explicit release, or failed checkout)
