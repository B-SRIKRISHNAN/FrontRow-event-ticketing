# Tasks: Backend Test Suite

**Input**: Design documents from `/specs/003-backend-test-suite/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend testing**: `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Test framework configuration and environment verification

- [x] T001 Verify test directory layout and environment configuration in `backend/tests/` and `backend/.env`
- [x] T002 [P] Verify Pytest async runner configuration in `backend/pytest.ini` / `backend/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared test fixtures and AsyncClient transport configuration

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Verify test database AsyncSession fixtures and `httpx.AsyncClient` transport setup in `backend/tests/conftest.py`

**Checkpoint**: Foundation ready - user story verification and implementation can now begin

---

## Phase 3: User Story 1 - Standalone Reviewer-Facing Concurrency Proof Suite (Priority: P1) 🎯 MVP

**Goal**: Deliver an individually runnable, standalone concurrency proof test (`pytest backend/tests/test_concurrency.py -v -s`) with extensive step-by-step console logging detailing setup, request dispatch, per-request resolution (HTTP `201` winner vs `409` conflict), and summary block confirming zero double-selling under simultaneous 15-request collision.

**Independent Test**: Execute `pytest tests/test_concurrency.py -v -s` from `backend/` and verify structured console output and 100% pass status.

### Implementation for User Story 1

- [x] T004 [P] [US1] Add connection pool size ($\ge 15$) precondition docstrings and architectural notes to `backend/tests/test_concurrency.py`
- [x] T005 [P] [US1] Implement structured Setup Phase console logging in `backend/tests/test_concurrency.py`
- [x] T006 [US1] Implement structured Dispatch Phase and Per-Request Resolution Phase console logging in `backend/tests/test_concurrency.py` (depends on T005)
- [x] T007 [US1] Implement formatted Summary Block console output and Constitution Principle V assertion checks in `backend/tests/test_concurrency.py` (depends on T006)
- [x] T008 [US1] Execute and verify standalone concurrency proof test via `pytest tests/test_concurrency.py -v -s` in `backend/tests/test_concurrency.py`

**Checkpoint**: User Story 1 (Concurrency Proof Test) is fully functional and independently testable with reviewer-readable console output.

---

## Phase 4: User Story 2 - Real-Database Integration & Lifecycle Test Track (Priority: P1) 🎯 MVP

**Goal**: Deliver comprehensive integration tests running against a genuine PostgreSQL database with Alembic migrations applied so that atomic hold acquisition, lazy expiration on read, atomic checkout with mock refund callbacks, and background lease sweeper recycling are verified end-to-end without DB mocking.

**Independent Test**: Execute `pytest tests/test_events.py tests/test_holds.py tests/test_checkout.py tests/test_sweeper.py -v` against migration-initialized PostgreSQL database.

### Implementation for User Story 2

- [x] T009 [P] [US2] Verify event listing and lazy expiration on read tests in `backend/tests/test_events.py`
- [x] T010 [P] [US2] Verify atomic hold acquisition and lock contention handling tests in `backend/tests/test_holds.py`
- [x] T011 [P] [US2] Verify atomic checkout, mock payment stub execution, order/ticket creation, and refund rollback tests in `backend/tests/test_checkout.py`
- [x] T012 [P] [US2] Verify background lease sweeper worker (`SKIP LOCKED`) recycling tests in `backend/tests/test_sweeper.py`
- [x] T013 [US2] Execute and verify full integration test track against PostgreSQL database (depends on T009, T010, T011, T012)

**Checkpoint**: User Story 2 (Integration Test Track) is fully verified against genuine PostgreSQL database without DB mocking.

---

## Phase 5: User Story 3 - Fast Unit & Validation Test Track (Priority: P2)

**Goal**: Deliver isolated unit tests covering Pydantic request/response schema validation, JWT auth token encoding/decoding, password hashing, and candidate seat matching algorithms providing rapid feedback (< 1.0s).

**Independent Test**: Execute `pytest tests/test_auth.py -v` without database connection overhead.

### Implementation for User Story 3

- [x] T014 [P] [US3] Verify password hashing (`bcrypt`), JWT claim decoding, and expiration check unit tests in `backend/tests/test_auth.py`
- [x] T015 [P] [US3] Verify Pydantic request payload validation rejection (`422 Unprocessable Entity`) in unit test module `backend/tests/test_auth.py`
- [x] T016 [US3] Execute and verify fast unit test track execution speed (< 1.0s) in `backend/tests/test_auth.py`

**Checkpoint**: All three user stories (US1, US2, US3) are fully functional and independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full suite regression verification and quickstart documentation alignment

- [x] T017 [P] Execute full backend test suite (`pytest tests/ -v`) and verify 100% pass rate under 20 seconds
- [x] T018 Run and validate all scenarios specified in `specs/003-backend-test-suite/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 (Concurrency Proof) and US2 (Integration Track) are P1 MVPs and can proceed in parallel
  - US3 (Unit Track) is P2 and can proceed in parallel or after US1/US2
- **Polish (Phase 6)**: Depends on completion of US1, US2, and US3

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on US1
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on US1/US2

### Parallel Opportunities

- Tasks T004, T005 in US1 can run in parallel
- Tasks T009, T010, T011, T012 in US2 can run in parallel across independent test files
- Tasks T014, T015 in US3 can run in parallel
- Task T017 in Polish can run in parallel with documentation checks

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational)
2. Complete Phase 3 (US1: Concurrency Proof Test)
3. Complete Phase 4 (US2: Integration Test Track)
4. Validate both MVP tracks against PostgreSQL
5. Complete Phase 5 (US3: Fast Unit Track) and Phase 6 (Polish)
