# Technical Research: LLM Engine Microservice

**Feature Branch**: `004-llm-engine-microservice`
**Date**: 2026-09-25

## 1. Swappable Provider Interface Architecture

### Problem Statement
Constitution Principle II requires the LLM engine to be strictly decoupled from direct database connectivity and backend domain logic. Furthermore, development and testing environments require offline capability (mocking), while production requires Google Gemini integration (`gemini-1.5-flash`).

### Research Findings & Decision
- **Decision**: Define an abstract base class `LLMProvider` in `llm-engine/app/providers/base.py` with an async method `parse_query(prompt: str) -> SeatSearchQuery`.
- **Implementations**:
  1. `GeminiProvider`: Uses the official `google-genai` SDK (`from google import genai`) configured with `GEMINI_API_KEY`. Utilizes structured JSON output mode (`response_schema=SeatSearchQuery`) to guarantee valid JSON responses matching Pydantic fields.
  2. `MockProvider`: Uses heuristic keyword matching ("2 seats", "together", "under $100", "Section A") to generate valid `SeatSearchQuery` objects for unit testing and offline development without consuming Gemini API quota.
- **Provider Selection**: Controlled via `LLM_PROVIDER=gemini` or `LLM_PROVIDER=mock` in `llm-engine/.env`.
- **Rationale**: Enables seamless testing without external network dependencies while providing native structured JSON generation when connected to Gemini.

## 2. System Prompt & Structured JSON Output Design

### Problem Statement
The LLM microservice must extract 4 key parameters from unconstrained natural language user input:
- `quantity` (integer $\ge 1$, default 1)
- `adjacency` (boolean, default false)
- `max_price` (optional float, e.g. 150.00)
- `preferred_section` (optional string, e.g. "Section A")

### Research Findings & Decision
- **Decision**: Implement a system prompt that explicitly instructs the LLM to act strictly as a ticket query parser:
  ```text
  You are a ticket query parser for FrontRow event ticketing.
  Extract search parameters from the user's prompt into JSON matching this exact schema:
  - quantity: Integer, number of tickets requested (default: 1)
  - adjacency: Boolean, true if user wants seats together/adjacent/next to each other (default: false)
  - max_price: Number or null, maximum price per ticket in dollars
  - preferred_section: String or null, preferred seating section or tier
  
  Do NOT include any commentary, Markdown tags, or conversational text. Return valid JSON only.
  ```
- **Gemini Config**: Pass `SeatSearchQuery` to Gemini's `config={"response_mime_type": "application/json", "response_schema": SeatSearchQuery}` so Gemini directly generates structured JSON conforming to the Pydantic type definitions.

## 3. Backend HTTP Client & Fallback Strategy

### Problem Statement
External LLM provider calls may suffer from latency spikes, rate limits, or network failures. Under no circumstances should LLM service degradation cause backend HTTP `500 Internal Server Error` responses.

### Research Findings & Decision
- **Decision**: Implement `LLMClient` in `backend/app/services/llm_client.py` using `httpx.AsyncClient` with:
  - `timeout=3.0` seconds
  - Explicit `try...except (httpx.TimeoutException, httpx.HTTPError, Exception)` wrapper.
  - On any error or timeout, log a warning and return a fallback `SeatSearchQuery(quantity=2, adjacency=True, max_price=None, preferred_section=None)` alongside a flag `fallback_to_manual=True`.
- **Rationale**: Protects system availability. If the LLM service is offline or slow, the user is seamlessly directed to manual seat map selection without noticing an API crash.

## 4. Row-as-Tier Contiguity Seat Matching Algorithm

### Problem Statement
Constitution Principle IV mandates that contiguity is defined strictly as consecutive `seat_number` values within the exact same `row`. Seats across different rows can NEVER be treated as contiguous.

### Research Findings & Decision
- **Decision**: Implement `SeatMatcher` in `backend/app/services/seat_matcher.py` with deterministic logic:
  1. Query available seats for event matching `max_price` and `preferred_section`, ordered strictly by `ORDER BY row ASC, seat_number ASC`.
  2. Group candidate seats by `row`.
  3. **If `adjacency == True`**:
     - For each row, iterate over seats and find the first contiguous block of size `quantity` where `seat_number[i+1] == seat_number[i] + 1` for all seats in the block.
     - Return the first contiguous block found (evaluated in `row ASC` order).
     - If no row contains a contiguous block of size `quantity`, return an empty list `[]` (triggering fallback to manual seat map selection).
  4. **If `adjacency == False`**:
     - First attempt to find a contiguous block in one row (preferred UX).
     - If no contiguous block exists, select the first `quantity` available seats in `row ASC, seat_number ASC` order regardless of row splits.
- **Rationale**: Eliminates ambiguous seat assignments and ensures physical venue realism.
