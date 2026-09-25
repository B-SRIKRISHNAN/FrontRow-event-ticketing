# Tasks: LLM Engine Microservice

**Input**: Design documents from `/specs/004-llm-engine-microservice/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **LLM Engine Microservice**: `llm-engine/`
- **Backend API**: `backend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Microservice initialization and environment configuration

- [x] T001 Verify microservice directory structure and dependencies in `llm-engine/pyproject.toml` and `llm-engine/.env.example`
- [x] T002 [P] Configure settings loader in `llm-engine/app/config.py` (`LLM_PROVIDER`, `GEMINI_API_KEY`, `PORT`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Pydantic schemas and abstract provider interface in LLM Engine microservice

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create Pydantic DTO models (`ParseQueryRequest`, `SeatSearchQuery`) in `llm-engine/app/schemas/query.py`
- [x] T004 [P] Create abstract `LLMProvider` base class interface in `llm-engine/app/providers/base.py`

**Checkpoint**: Foundation ready - provider implementations and endpoints can now begin

---

## Phase 3: User Story 1 - Natural Language Ticket Query Parsing via Isolated LLM Engine (Priority: P1) 🎯 MVP

**Goal**: Deliver a standalone, decoupled LLM Engine microservice running in `llm-engine/` with zero database connectivity, featuring swappable providers (`GeminiProvider` default, `MockProvider` offline) parsing query prompts into validated `SeatSearchQuery` JSON schemas.

**Independent Test**: Execute `pytest tests/ -v` inside `llm-engine/` or curl `POST http://localhost:8001/api/v1/parse-query`.

### Implementation for User Story 1

- [x] T005 [P] [US1] Implement `MockProvider` with heuristic query parsing in `llm-engine/app/providers/mock.py`
- [x] T006 [P] [US1] Implement `GeminiProvider` using `google-genai` SDK and structured JSON output mode in `llm-engine/app/providers/gemini.py`
- [x] T007 [US1] Implement provider factory and API routes (`POST /api/v1/parse-query`, `GET /health`) in `llm-engine/app/api/routes.py` (depends on T004, T005, T006)
- [x] T008 [US1] Assemble FastAPI application entrypoint in `llm-engine/app/main.py`
- [x] T009 [P] [US1] Create unit tests for mock and gemini providers in `llm-engine/tests/test_parse_query.py`
- [x] T010 [US1] Execute and verify standalone microservice tests in `llm-engine/tests/test_parse_query.py`

**Checkpoint**: User Story 1 (LLM Microservice) is fully functional and independently testable on port 8001.

---

## Phase 4: User Story 2 - Backend Integration & Fault-Tolerant Microservice Communication (Priority: P1) 🎯 MVP

**Goal**: Deliver backend HTTP integration connecting `backend/` to `llm-engine/` with a 3.0s timeout and exception handling that gracefully falls back to manual seat map selection (`fallback_to_manual=True`) on LLM failure without throwing HTTP 500 errors.

**Independent Test**: Simulate LLM service timeout or disconnection and verify that `POST /api/v1/events/1/ai-search` returns HTTP `200 OK` with `fallback_to_manual: true`.

### Implementation for User Story 2

- [x] T011 [P] [US2] Add `LLM_ENGINE_URL` configuration to `backend/app/config.py` and `backend/.env.example`
- [x] T012 [P] [US2] Implement `LLMClient` with `httpx.AsyncClient`, 3.0s timeout, and fallback handling in `backend/app/services/llm_client.py`
- [x] T013 [US2] Update `POST /api/v1/events/{id}/ai-search` in `backend/app/api/v1/events.py` to call `LLMClient` (depends on T012)
- [x] T014 [P] [US2] Create integration tests for LLM client integration and failure fallback in `backend/tests/test_llm_client.py`
- [x] T015 [US2] Execute and verify backend LLM client fallback tests in `backend/tests/test_llm_client.py`

**Checkpoint**: User Story 2 (Backend RPC Integration & Fallback) is fully functional and fault-tolerant.

---

## Phase 5: User Story 3 - Deterministic Contiguity & Candidate Seat Matching Engine (Priority: P2)

**Goal**: Finalize candidate seat matching logic against Constitution Principle IV rules (row-as-tier contiguity, `ORDER BY row ASC, seat_number ASC`, zero cross-row seat splits when `adjacency=true`, non-contiguous fallback when `adjacency=false`).

**Independent Test**: Invoke seat search against an event seat map with fragmented vs contiguous availability and verify row contiguity.

### Implementation for User Story 3

- [x] T016 [P] [US3] Implement `SeatMatcher` contiguity and candidate matching engine in `backend/app/services/seat_matcher.py`
- [x] T017 [US3] Connect `SeatMatcher` into `POST /api/v1/events/{id}/ai-search` endpoint in `backend/app/api/v1/events.py` (depends on T013, T016)
- [x] T018 [P] [US3] Create unit and integration tests for contiguity matching in `backend/tests/test_seat_matcher.py`
- [x] T019 [US3] Execute and verify seat matcher contiguity test suite in `backend/tests/test_seat_matcher.py`

**Checkpoint**: All three user stories (US1, US2, US3) are fully integrated, matching contiguous seats deterministically.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full system verification across backend and microservice tracks

- [x] T020 [P] Execute full test suite across both `llm-engine/` and `backend/` services
- [x] T021 Run and validate all scenarios specified in `specs/004-llm-engine-microservice/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 (LLM Microservice) and US2 (Backend RPC) are P1 MVPs
  - US3 (Seat Matcher Contiguity) depends on US1 & US2 backend integration
- **Polish (Phase 6)**: Depends on completion of US1, US2, and US3

### Parallel Opportunities

- Tasks T005, T006 in US1 can run in parallel
- Tasks T011, T012, T014 in US2 can run in parallel
- Tasks T016, T018 in US3 can run in parallel
- Task T020 in Polish can run in parallel with documentation checks
