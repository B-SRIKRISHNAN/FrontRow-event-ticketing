# Feature Specification: LLM Engine Microservice

**Feature Branch**: `004-llm-engine-microservice`

**Created**: 2026-09-25

**Status**: Draft

**Input**: User description: "Spec 4 — LLM Engine Microservice: Swappable provider interface, default Gemini (Principle II isolation, Principle VI Pydantic output schema). Prompt design for {quantity, adjacency, max_price, preferred_section}. Swap backend's Spec 2 stub for a real call to this service; timeout/failure handling exercised end-to-end. Adjacency/contiguity matching logic finalized against constitution Principle IV rules (row-as-tier, per-row seat numbering, no cross-row splits)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Ticket Query Parsing via Isolated LLM Engine (Priority: P1) 🎯 MVP

As an event ticket buyer, I want to type natural language requests (e.g. "Find me 2 seats together in Section A under $150") into the search bar so that an isolated LLM microservice extracts structured search criteria (`quantity`, `adjacency`, `max_price`, `preferred_section`) into a strictly validated Pydantic schema without accessing database storage directly.

**Why this priority**: Constitution Principle II & IV requirement. Provides intelligent natural language ticket search capabilities while guaranteeing strict architectural isolation between the LLM parser and database storage.

**Independent Test**: Can be tested independently by sending HTTP `POST /api/v1/parse-query` requests with natural language prompts to the LLM microservice and asserting that returned JSON payloads match the Pydantic schema structure.

**Acceptance Scenarios**:

1. **Given** a natural language query specifying quantity, budget, section, and seat togetherness (e.g. "2 tickets together near Section B for under $100"), **When** processed by the LLM microservice, **Then** it returns structured JSON with `quantity: 2`, `adjacency: true`, `max_price: 100.0`, `preferred_section: "Section B"`.
2. **Given** a vague or minimal query (e.g. "front row seats"), **When** processed by the LLM microservice, **Then** omitted parameters return as `null` or safe defaults (`quantity: 1`, `adjacency: false`, `max_price: null`, `preferred_section: null`) without validation errors.
3. **Given** the LLM engine microservice architecture, **When** inspected, **Then** the microservice possesses zero database connection settings, zero ORM models, and zero direct database access capabilities (Principle II).

---

### User Story 2 - Backend Integration & Fault-Tolerant Microservice Communication (Priority: P1) 🎯 MVP

As a ticket buyer using the Backend API, I want natural language search requests (`POST /api/v1/events/{id}/search-seats`) to call the live LLM microservice with end-to-end timeout and error handling so that LLM service downtime or invalid output gracefully falls back to manual seat map selection without failing the request with HTTP 500.

**Why this priority**: Guarantees system resilience and high availability even when external LLM providers experience latency spikes, rate limits, or network failures.

**Independent Test**: Can be tested independently by simulating LLM microservice timeouts, 500 errors, or network disconnections during backend seat search calls and asserting that the backend returns an empty candidate list (`200 OK` with `fallback_to_manual: true` or empty array) rather than an unhandled server error.

**Acceptance Scenarios**:

1. **Given** a healthy LLM microservice instance, **When** `POST /api/v1/events/{id}/search-seats` is invoked with a prompt, **Then** the backend calls the microservice, receives structured search parameters, executes database candidate seat matching, and returns candidate seat objects.
2. **Given** the LLM microservice times out (> 3 seconds) or fails with an HTTP error, **When** `POST /api/v1/events/{id}/search-seats` is invoked, **Then** the backend logs the warning, gracefully catches the exception, and returns HTTP `200 OK` with `fallback_to_manual: true` and an empty seat list.
3. **Given** an environment configuration change, **When** `LLM_PROVIDER` is set to `gemini` or `mock`, **Then** the microservice switches provider implementations via a swappable interface without code modifications.

---

### User Story 3 - Deterministic Contiguity & Candidate Seat Matching Engine (Priority: P2)

As a ticket buyer, I want candidate seats matched against parsed criteria to strictly enforce row-as-tier contiguity rules (consecutive `seat_number` values within the exact same `row`) so that group seats are never split across different rows when `adjacency=true`.

**Why this priority**: Ensures physical venue realism and guarantees that group ticket buyers receive adjacent seats in the exact same row.

**Independent Test**: Can be tested independently by invoking seat search against an event seat map containing fragmented vs contiguous seat availability across multiple rows.

**Acceptance Scenarios**:

1. **Given** a search request with `quantity: 3` and `adjacency: true`, **When** candidate seat matching runs, **Then** the algorithm evaluates rows in ascending order (`ORDER BY row ASC, seat_number ASC`) and returns 3 seats with consecutive `seat_number` values in the exact same `row`.
2. **Given** a search request with `quantity: 3` and `adjacency: true` where no single row has 3 consecutive available seats, **When** candidate seat matching runs, **Then** the algorithm returns zero seats (empty list) to trigger manual seat map fallback rather than splitting the 3 seats across separate rows.
3. **Given** a search request with `quantity: 3` and `adjacency: false`, **When** candidate seat matching runs, **Then** the algorithm prefers contiguous seats in one row if available, but falls back to non-contiguous matching ordered strictly by `row ASC, seat_number ASC` if no contiguous block exists.

---

### Edge Cases

- What happens if the LLM provider API key is missing or invalid? The microservice raises a structured startup/request exception, and the Backend API gracefully falls back to manual seat selection.
- What happens if the user query contains prompt injection or non-search text? The LLM system prompt constrains output strictly to JSON schemas, returning `null` fields for non-ticket intent.
- What happens if a seat row has non-consecutive seat numbering (e.g. seats 1, 2, 4 available)? The contiguity algorithm checks `seat_number[i+1] == seat_number[i] + 1` and rejects non-consecutive gaps.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST maintain a standalone, decoupled LLM Engine microservice running in `llm-engine/` with zero database connectivity or ORM models (Principle II).
- **FR-002**: LLM Engine microservice MUST expose a swappable provider interface (`LLMProvider`) supporting Google Gemini (`gemini-1.5-flash` / default) and a local mock provider (`mock`) configurable via environment variables.
- **FR-003**: LLM Engine microservice MUST parse natural language search queries into structured JSON strictly validated against a Pydantic schema (`quantity: int`, `adjacency: bool`, `max_price: float | null`, `preferred_section: str | null`).
- **FR-004**: Backend API MUST replace its Spec 2 search stub with live HTTP calls to `POST /api/v1/parse-query` on the LLM Engine microservice.
- **FR-005**: Backend API MUST implement an HTTP timeout threshold (default 3.0s) and exception handling for LLM microservice calls, falling back to manual seat map selection (`fallback_to_manual: true`) on timeout or error.
- **FR-006**: Candidate seat matching algorithm MUST enforce row-as-tier contiguity: contiguous seats MUST belong to the exact same `row` with consecutive `seat_number` values (`seat_number[i+1] == seat_number[i] + 1`). Seats in different rows MUST NEVER be grouped as contiguous.
- **FR-007**: When `adjacency=true`, the matching algorithm MUST return a single contiguous block of `quantity` seats in one row, or return an empty list if no such block exists.
- **FR-008**: Candidate seat selection queries MUST evaluate available seats using deterministic ordering (`ORDER BY row ASC, seat_number ASC`).

### Key Entities *(include if feature involves data)*

- **Natural Language Search Query**: Incoming user text prompt describing desired ticket count, budget, section, and seating preference.
- **Parsed Seat Search Parameters (Pydantic Model)**: Structured DTO containing `quantity` (int, default 1), `adjacency` (bool, default false), `max_price` (Optional[float]), and `preferred_section` (Optional[str]).
- **Candidate Seat Match**: Set of physical `Seat` objects matching parsed query criteria and event availability.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: LLM microservice parses natural language queries and returns validated Pydantic JSON structures in under 1.5 seconds p95.
- **SC-002**: 100% of LLM service timeouts, network failures, or invalid responses trigger graceful manual seat selection fallback without returning HTTP 500 errors to the client.
- **SC-003**: 100% of adjacent seat recommendations satisfy single-row consecutive seat numbering (`seat_number[i+1] == seat_number[i] + 1`) without cross-row splits.

## Assumptions

- Google Gemini API key (`GEMINI_API_KEY`) is provided in `.env` for production/live LLM mode; mock provider is available for offline/testing mode.
- FastAPI framework and Pydantic v2 are utilized for microservice request handling and output schema validation.
- Backend API and LLM Engine communicate via HTTP REST endpoints (`http://llm-engine:8001` or `http://localhost:8001`).
