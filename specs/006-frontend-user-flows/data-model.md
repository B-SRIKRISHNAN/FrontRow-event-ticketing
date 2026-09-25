# Data Model & State Specification: Frontend User Flows

**Feature Branch**: `006-frontend-user-flows`
**Date**: 2026-09-25

## 1. Page State Models

### Seat Map Page State (`/events/[id]/page.js`)
```javascript
{
  event: { id: 1, title: "...", venue_name: "..." },
  seats: [
    { id: 1, row: "A", seat_number: 1, section: "A", price: "150.00", status: "AVAILABLE", current_hold_id: null },
    ...
  ],
  selectedSeatIds: [1, 2],
  activeHold: {
    hold_id: "c7b3e102-...",
    expires_at: "2026-09-25T20:40:00Z",
    seat_ids: [1, 2],
    status: "ACTIVE"
  },
  aiSearchQuery: "2 seats together under $150",
  toast: { message: "Hold acquired for 5 minutes!", type: "success" },
  loading: false,
  pollingActive: true
}
```

---

## 2. End-to-End User Flow Sequence

```mermaid
sequenceDiagram
    autonumber
    participant User as Ticket Buyer
    participant FE as Next.js Frontend
    participant Auth as Auth Store (lib/auth.js)
    participant API as FastAPI Backend (:8000)
    participant LLM as LLM Engine (:8001)

    %% Step 1: Login
    User->>FE: Navigate to /login & submit credentials
    FE->>API: POST /api/v1/auth/login {email, password}
    API-->>FE: HTTP 200 OK {access_token: "jwt_..."}
    FE->>Auth: setToken("jwt_..."), setUser({email})
    FE->>User: Redirect to /events

    %% Step 2: Browse Events & View Map
    User->>FE: Click Event -> Navigate to /events/1
    FE->>API: GET /api/v1/events/1/seats
    API-->>FE: HTTP 200 OK SeatMapResponse
    FE->>User: Render SeatGridCell grid

    loop Every 4 Seconds (Background Polling)
        FE->>API: GET /api/v1/events/1/seats
        API-->>FE: Live Seat States
        FE->>FE: Update Seat Map UI without flicker
    end

    %% Step 3: AI Search (Optional)
    opt AI Candidate Seat Search
        User->>FE: Type "2 seats together under $150" -> Click AI Search
        FE->>API: POST /api/v1/events/1/ai-search {query: "..."}
        API->>LLM: POST /api/v1/parse-query {query: "..."}
        LLM-->>API: SeatSearchQuery
        API-->>FE: AISearchResponse {recommended_seat_ids: [1, 2]}
        FE->>User: Highlight Candidate Seats [1, 2]
    end

    %% Step 4: Hold Acquisition
    User->>FE: Select Seat IDs [1, 2] -> Click "Hold Seats"
    FE->>API: POST /api/v1/events/1/holds {seat_ids: [1, 2]} (Bearer Token)
    API-->>FE: HTTP 201 Created {hold_id: "...", expires_at: "..."}
    FE->>User: Render CountdownTimer (5 min lease) & Checkout Button

    %% Step 5: Checkout
    User->>FE: Click "Complete Checkout"
    FE->>API: POST /api/v1/checkout/holds/{holdId} {payment_token: "mock_token_ok"}
    API-->>FE: HTTP 200 OK OrderResponse {id: 1, tickets: [...]}
    FE->>User: Display Toast Success & Redirect to /orders
```
