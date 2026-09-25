# Implementation Plan: LLM Engine Microservice

**Branch**: `004-llm-engine-microservice` | **Date**: 2026-09-25 | **Spec**: [specs/004-llm-engine-microservice/spec.md](file:///d:/projects/interviews/FrontRow-event-ticketing/specs/004-llm-engine-microservice/spec.md)

**Input**: Feature specification from `/specs/004-llm-engine-microservice/spec.md`

## Summary

The LLM Engine Microservice feature implements an isolated, standalone FastAPI microservice in `llm-engine/` that extracts structured seat search parameters (`quantity`, `adjacency`, `max_price`, `preferred_section`) from natural language queries using Google Gemini (with a swappable mock provider for testing). It enforces Principle II by possessing zero database connectivity or ORM models. The Backend API replaces its Spec 2 search stub with a live HTTP client call to `http://localhost:8001/api/v1/parse-query` with a 3.0-second timeout and graceful fallback to manual seat map selection. Candidate seat matching logic is finalized against Constitution Principle IV contiguity rules (`ORDER BY row ASC, seat_number ASC`, row-as-tier contiguity, zero cross-row seat splits).

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**:
- Microservice: `fastapi`, `uvicorn`, `pydantic>=2.6.0`, `google-genai>=0.1.0`, `httpx`
- Backend Integration: `httpx` (AsyncClient for microservice RPC)

**Storage**: None in `llm-engine/` (Principle II absolute database isolation). Backend API uses PostgreSQL.

**Testing**: `pytest`, `pytest-asyncio`, `httpx`

**Target Platform**: Windows / Linux server environment (runs as standalone microservice on port 8001)

**Project Type**: Microservice (`llm-engine/`) + Backend API Integration (`backend/app/services/llm_client.py`)

**Performance Goals**: Query parsing < 1.5s p95; backend client timeout threshold = 3.0s

**Constraints**: Zero database connectivity or secrets in `llm-engine/`; Pydantic schema validation across all responses; strict row-as-tier contiguity (no cross-row splits when `adjacency=true`)

**Scale/Scope**: 1 dedicated microservice repository folder (`llm-engine/`), 1 client integration module (`backend/app/services/llm_client.py`), candidate seat matching algorithm in backend

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Absolute Concurrency & Double-Selling Immunity)**: ✅ PASS. Candidate seat matching produces candidate IDs; hold acquisition and locking remain strictly handled by backend ACID transactions.
- **Principle II (Clean Architectural Separation & LLM Isolation)**: ✅ PASS. LLM microservice has ZERO database connections or ORM models. Frontend communicates strictly with Backend API; Backend API calls LLM microservice over internal HTTP.
- **Principle III (Tri-Layer Lease Lifecycle Management)**: ✅ PASS. Seat search reads available seat states without creating holds or altering lease timestamps.
- **Principle IV (Deterministic Candidate Seat Matching & AI Parsing Boundary)**: ✅ PASS. Prompt engineering and Pydantic validation extract `{quantity, adjacency, max_price, preferred_section}`. Contiguity algorithm enforces row-as-tier (`ORDER BY row ASC, seat_number ASC`, consecutive `seat_number` values within exact same `row`). LLM failure gracefully falls back to manual selection.
- **Principle V (Empirical Automated Concurrency Verification)**: ✅ PASS. Automated tests verify fallback behavior and candidate seat matching.
- **Principle VI (Mandatory Pydantic Schema Validation)**: ✅ PASS. Microservice enforces Pydantic `SeatSearchQuery` output model; backend validates incoming response.
- **Principle VII (Zero Secret Leakage)**: ✅ PASS. `GEMINI_API_KEY` stored exclusively in `.env` / environment; `.env.example` committed with placeholder values only.
- **Principle VIII (Strict Alembic Migrations)**: ✅ PASS. No database schema changes required for microservice integration.

## Project Structure

### Documentation (this feature)

```text
specs/004-llm-engine-microservice/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── llm_engine_api.md# Microservice HTTP API OpenAPI/Pydantic contract
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
llm-engine/
├── .env.example              # Provider config (LLM_PROVIDER=gemini|mock, PORT=8001)
├── pyproject.toml            # Dependencies (fastapi, google-genai, pydantic)
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI application entrypoint
│   ├── config.py             # Settings loading (LLM_PROVIDER, GEMINI_API_KEY, PORT)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── query.py          # Pydantic models: ParseQueryRequest, SeatSearchQuery
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract LLMProvider interface
│   │   ├── gemini.py         # Google Gemini provider implementation (google-genai SDK)
│   │   └── mock.py           # Mock provider for offline/testing mode
│   └── api/
│       ├── __init__.py
│       └── routes.py         # POST /api/v1/parse-query
└── tests/
    ├── conftest.py
    └── test_parse_query.py   # Unit & provider tests for LLM microservice

backend/
├── app/
│   ├── config.py             # Add LLM_ENGINE_URL="http://localhost:8001"
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_client.py     # Async HTTP client calling LLM microservice with timeout & fallback
│   │   └── seat_matcher.py   # Deterministic contiguity seat matching algorithm (Principle IV)
│   └── api/v1/
│       └── events.py         # Update POST /events/{id}/ai-search to call LLM client & matcher
└── tests/
    └── test_ai_search.py     # Integration tests for backend AI search endpoint & fallback logic
```

**Structure Decision**: Decoupled microservice folder (`llm-engine/`) alongside existing `backend/` service, communicating via internal HTTP REST calls.

## Complexity Tracking

*No constitution violations present. All architectural decisions align strictly with Principles I–VIII.*
