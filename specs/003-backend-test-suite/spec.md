# Feature Specification: Backend Test Suite

**Feature Branch**: `003-backend-test-suite`

**Created**: 2026-09-25

**Status**: Draft

**Input**: User description: "Spec 3 — Backend Test Suite: Two separate tracks - Unit tests (service/controller, mocked DB) and Integration/concurrency tests (real Postgres DB). Standalone reviewer-facing concurrency proof test in backend/tests/test_concurrency.py with extensive step-by-step console logging and connection pool precondition notes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Standalone Reviewer-Facing Concurrency Proof Suite (Priority: P1) 🎯 MVP

As a code reviewer or evaluator, I want an individually runnable, standalone concurrency proof test (`pytest backend/tests/test_concurrency.py -v`) with extensive step-by-step console logging so that I can empirically verify 10+ simultaneous collision immunity, lock contention resolution, and zero double-selling without needing to read assertion code alone.

**Why this priority**: Constitution Principle V and project requirement. Provides empirical, reviewer-facing proof of double-selling immunity under simultaneous collision.

**Independent Test**: Can be tested independently by running `pytest tests/test_concurrency.py -v -s` from `backend/` and observing structured, step-by-step console logs detailing setup, dispatch, per-request resolution, and a final summary block.

**Acceptance Scenarios**:

1. **Given** a target seat in `AVAILABLE` state, **When** 10+ simultaneous hold requests target the exact same seat at the exact same millisecond, **Then** the test logs the setup state, logs each request dispatch with timestamp/index, logs each per-request outcome (`201 Created` winner vs `409 Conflict` rejections and lock contention path), and outputs a final summary block confirming exactly 1 winner, zero double-holds, and seat `LOCKED` state.
2. **Given** the concurrency test file `backend/tests/test_concurrency.py`, **When** inspected by a reviewer, **Then** it contains explicit documentation explaining that SQLAlchemy connection pool sizing ($\ge 15$) is a mandatory precondition for test validity to avoid app-layer bottlenecking prior to reaching PostgreSQL's lock manager.
3. **Given** existing integration and unit test cases, **When** the concurrency proof test suite is executed, **Then** existing tests remain intact and complementary without unnecessary deletion or breakage.

---

### User Story 2 - Real-Database Integration & Lifecycle Test Track (Priority: P1) 🎯 MVP

As a developer, I want comprehensive integration tests running against a genuine PostgreSQL database with Alembic migrations applied so that atomic hold acquisition, lazy expiration on read, atomic checkout with mock refund callbacks, explicit hold release, and asynchronous lease sweeper recycling are verified end-to-end.

**Why this priority**: Guarantees system correctness across database transactions, non-blocking row locks, and background worker cleanup without mocking database behavior.

**Independent Test**: Can be tested independently by running `pytest tests/test_events.py tests/test_holds.py tests/test_checkout.py tests/test_sweeper.py` against a migration-initialized PostgreSQL database.

**Acceptance Scenarios**:

1. **Given** an active event and seat map, **When** `GET /events/{id}/seats` is invoked on seats with expired holds, **Then** the test verifies seats are projected as `AVAILABLE` via lazy expiration on read without database write operations.
2. **Given** an active hold, **When** checkout is submitted before lease expiration, **Then** the test verifies seats transition to `SOLD`, hold transitions to `COMPLETED` with `order_id`, and tickets are generated.
3. **Given** a hold that expires before checkout completes, **When** checkout is attempted, **Then** the test verifies zero seat rows are updated, the transaction rolls back, hold status is marked `EXPIRED`, `409 Conflict` is returned, and a mock refund callback is triggered.
4. **Given** an expired hold, **When** the background lease sweeper worker executes a pass (`SKIP LOCKED`), **Then** the test verifies seats return to `AVAILABLE` status and hold status is set to `EXPIRED`.

---

### User Story 3 - Fast Unit & Validation Test Track (Priority: P2)

As a developer, I want isolated unit tests covering Pydantic request/response schema validation, JWT auth token encoding/decoding, password hashing, and candidate seat matching algorithms so that fast feedback is provided without requiring database connection setups.

**Why this priority**: Ensures rapid developer feedback and regression protection for non-database domain logic and API schemas.

**Independent Test**: Can be tested independently by executing unit test modules (`pytest tests/test_auth.py`) without database transaction overhead.

**Acceptance Scenarios**:

1. **Given** registration and login payloads, **When** unit tests evaluate password hashing (`bcrypt`) and JWT token encoding/decoding, **Then** claims decoding, expiration checks, and invalid token rejection pass cleanly.
2. **Given** invalid or malformed request payloads (e.g., missing email, password under 8 characters, invalid seat IDs), **When** sent to endpoints, **Then** Pydantic validation rejects requests with HTTP `422 Unprocessable Entity` or `400 Bad Request`.

---

### Edge Cases

- What happens if the connection pool size is less than the number of concurrent collision requests? The test documents this precondition and warns that a small pool bottlenecks at the app connection queue before reaching PostgreSQL's row lock manager (`55P03`).
- What happens if console output is captured by default in pytest? The concurrency proof test is designed with structured `print()` logging readable under `pytest -s` or `-v`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST maintain two explicitly separate test tracks: fast unit tests (service/controller/auth logic) and real-database integration/concurrency tests.
- **FR-002**: System MUST provide a dedicated, standalone concurrency proof test in `backend/tests/test_concurrency.py` that can be executed individually via `pytest tests/test_concurrency.py -v`.
- **FR-003**: The standalone concurrency proof test MUST produce extensive, step-by-step console logging detailing:
  - *Setup Phase*: Seed state confirmation, target seat ID, and initial seat status.
  - *Dispatch Phase*: Each of the 10+ concurrent requests logged as fired with index and timestamp.
  - *Per-Request Outcome Phase*: Resolution of each request (`201 Created` winner vs `409 Conflict` rejections, and lock-contention details).
  - *Summary Block*: Aggregated statistics ("14/15 correctly rejected, 1/15 succeeded, seat X now LOCKED with hold Y, zero double-holds detected").
- **FR-004**: `backend/tests/test_concurrency.py` MUST contain explicit code comments and docstrings stating that connection pool sizing ($\ge 15$) is a mandatory precondition for concurrency test validity.
- **FR-005**: Integration tests (`test_holds.py`, `test_checkout.py`, `test_events.py`, `test_sweeper.py`) MUST run against a genuine PostgreSQL database with Alembic migrations applied, with zero database mocking permitted for database locking, transactions, or worker tasks.
- **FR-006**: Existing test cases MUST be preserved and complemented without unnecessary removal or regression.

### Key Entities *(include if feature involves data)*

- **Concurrency Proof Logger**: Structured logger/print formatter outputting step-by-step execution traces during collision testing.
- **Test Database Context**: Ephemeral/genuine PostgreSQL connection context running Alembic migrations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% pass rate across the full backend test suite (`pytest`) in under 20 seconds.
- **SC-002**: `backend/tests/test_concurrency.py` produces reviewer-readable console logs clearly documenting setup, dispatch, per-request outcomes, and final summary block.
- **SC-003**: 100% of integration test suites run against genuine PostgreSQL without DB mocking errors.

## Assumptions

- PostgreSQL database server is running locally or in CI with Spec 1 schema migrations applied.
- Backend dependencies (`pytest`, `pytest-asyncio`, `httpx`) are installed via `uv sync --extra dev`.
- Standard connection pool configuration (`pool_size=15`, `max_overflow=10`) is maintained in `backend/.env`.
