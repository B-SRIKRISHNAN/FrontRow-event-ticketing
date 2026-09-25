# Data Model & Schema Specification: LLM Engine Microservice

**Feature Branch**: `004-llm-engine-microservice`
**Date**: 2026-09-25

## 1. Pydantic DTO Schemas

### Microservice Request Payload (`ParseQueryRequest`)
```python
class ParseQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")
```

### Microservice Output Payload (`SeatSearchQuery`)
```python
class SeatSearchQuery(BaseModel):
    quantity: int = Field(default=1, ge=1, description="Number of tickets requested")
    adjacency: bool = Field(default=False, description="True if seats must be adjacent/together")
    max_price: Optional[float] = Field(default=None, description="Maximum price per ticket")
    preferred_section: Optional[str] = Field(default=None, description="Preferred seating section or row prefix")
```

### Backend API Search Response DTO (`AISearchResponse`)
```python
class AISearchResponse(BaseModel):
    quantity: int
    adjacency: bool
    max_price: Optional[float] = None
    preferred_section: Optional[str] = None
    recommended_seat_ids: List[int] = Field(default_factory=list)
    fallback_to_manual: bool = Field(default=False, description="True if manual seat map selection is recommended")
```

---

## 2. Row-as-Tier Contiguity Matching Flow

```mermaid
flowchart TD
    A[Start Seat Search] --> B[Fetch Available Seats ORDER BY row ASC, seat_number ASC]
    B --> C{Filter by max_price & preferred_section}
    C --> D[Group Available Seats by Row]
    D --> E{Is adjacency == True?}

    E -- Yes --> F[Scan Each Row for Contiguous Block of size 'quantity']
    F --> G{Contiguous Block Found in Same Row?}
    G -- Yes --> H[Return Seat IDs of Contiguous Block]
    G -- No --> I[Return Empty List & Set fallback_to_manual = True]

    E -- No --> J[Attempt Contiguous Block in Same Row]
    J --> K{Contiguous Block Found?}
    K -- Yes --> H
    K -- No --> L[Fallback: Pick Top 'quantity' Seats by row ASC, seat_number ASC]
    L --> M[Return Picked Seat IDs]
```

---

## 3. Microservice vs Backend Decoupling Architecture

```mermaid
sequenceDiagram
    autonumber
    participant Client as Frontend / User
    participant Backend as Backend API (FastAPI)
    participant LLM as LLM Engine (FastAPI :8001)
    participant Gemini as Google Gemini API
    participant DB as PostgreSQL Database

    Client->>Backend: POST /api/v1/events/{id}/ai-search {"query": "2 seats together under $100"}
    Backend->>LLM: POST /api/v1/parse-query {"query": "2 seats together under $100"} (Timeout: 3s)
    
    alt LLM Healthy
        LLM->>Gemini: generate_content(prompt, schema=SeatSearchQuery)
        Gemini-->>LLM: JSON {"quantity": 2, "adjacency": true, "max_price": 100.0, "preferred_section": null}
        LLM-->>Backend: HTTP 200 OK {"quantity": 2, "adjacency": true, ...}
    else LLM Timeout / Error
        LLM--xBackend: Timeout / Connection Error
        Backend->>Backend: Log Warning & set fallback_to_manual = True
    end

    Backend->>DB: Query Available Seats (ORDER BY row ASC, seat_number ASC)
    DB-->>Backend: Seat Rows
    Backend->>Backend: Execute SeatMatcher Contiguity Logic
    Backend-->>Client: HTTP 200 OK AISearchResponse(recommended_seat_ids=[...], fallback_to_manual=...)
```
