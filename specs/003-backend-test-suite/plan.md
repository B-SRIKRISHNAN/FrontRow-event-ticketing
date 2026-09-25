# Implementation Plan: Backend Test Suite

**Branch**: `003-backend-test-suite` | **Date**: 2026-09-25 | **Spec**: [specs/003-backend-test-suite/spec.md](file:///d:/projects/interviews/FrontRow-event-ticketing/specs/003-backend-test-suite/spec.md)

**Input**: Feature specification from `/specs/003-backend-test-suite/spec.md`

## Summary

The Backend Test Suite feature establishes a comprehensive, non-regressive testing framework for FrontRow's FastAPI backend service. The suite is divided into two distinct tracks: (1) fast unit tests covering auth, JWT, validation, and seat-matching algorithms with mocked dependencies, and (2) real-database integration and concurrency tests executing against genuine PostgreSQL database instances with Alembic migrations applied. Crucially, a standalone, reviewer-facing concurrency proof test (`backend/tests/test_concurrency.py`) is implemented to provide structured, step-by-step console logging detailing setup, request dispatch, per-request resolution (HTTP `201` winner vs HTTP `409` lock contention), and a summary block confirming zero double-selling under simultaneous 15-request collision.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: `pytest`, `pytest-asyncio`, `httpx`, `sqlalchemy` (async engine with `asyncpg`), `fastapi`, `pydantic`

**Storage**: PostgreSQL (ephemeral/genuine test DB with Alembic migrations applied)

**Testing**: `pytest` async runner with `asyncio.gather` for simultaneous request dispatch

**Target Platform**: Windows / Linux server environment (local dev & CI)

**Project Type**: Web service backend test suite (`backend/tests/`)

**Performance Goals**: Full suite execution < 20 seconds; concurrency test execution < 3 seconds

**Constraints**: Zero DB mocking for integration and concurrency tests; SQLAlchemy connection pool size ($\ge 15$) precondition strictly documented; zero deletion of pre-existing valid tests

**Scale/Scope**: 15 simultaneous collision requests targeting single AVAILABLE seat at identical millisecond timestamp

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Absolute Concurrency & Double-Selling Immunity)**: ✅ PASS. The test suite verifies deterministic row locking (`SELECT FOR UPDATE OF seats NOWAIT`), atomic seat state transitions, zero double-selling, and lock failure handling returning HTTP `409 Conflict`.
- **Principle II (Clean Architectural Separation & Security)**: ✅ PASS. Tests verify JWT identity enforcement (claims extraction) and prohibit client-supplied `user_id` query/body parameters.
- **Principle III (Tri-Layer Lease Lifecycle Management)**: ✅ PASS. Integration tests cover lazy expiration on read, atomic overwrite on lock acquisition, and asynchronous sweeper cleanup (`SKIP LOCKED`).
- **Principle IV (Deterministic Candidate Seat Matching & AI Parsing Boundary)**: ✅ PASS. Unit tests verify Pydantic payload validation and seat adjacency matching across rows.
- **Principle V (Empirical Automated Concurrency Verification)**: ✅ PASS. `backend/tests/test_concurrency.py` acts as the dedicated empirical proof artifact with step-by-step reviewer logging.
- **Principle VI (Mandatory Pydantic Schema Validation)**: ✅ PASS. Unit tests assert validation errors (`422 Unprocessable Entity`) on malformed request bodies.
- **Principle VII (Zero Secret Leakage)**: ✅ PASS. Tests use test environment variables loaded safely without committing secrets or credentials.
- **Principle VIII (Strict Alembic Migrations)**: ✅ PASS. Integration tests execute against real PostgreSQL initialized via Alembic schema migrations.

## Project Structure

### Documentation (this feature)

```text
specs/003-backend-test-suite/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── test_cli.md      # Test execution CLI specification
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── tests/
│   ├── conftest.py            # Test database session & async HTTP client fixtures
│   ├── test_auth.py           # Unit track: JWT claims, bcrypt password hashing, auth validation
│   ├── test_events.py         # Integration track: Event listing, seat map fetching, lazy expiry read
│   ├── test_holds.py          # Integration track: Hold creation, collision handling, lease expiration
│   ├── test_checkout.py       # Integration track: Payment stub, hold completion, seat SOLD transition, refund rollback
│   ├── test_sweeper.py        # Integration track: Background lease sweeper worker (SKIP LOCKED)
│   └── test_concurrency.py    # Standalone Concurrency Proof: Step-by-step console logging collision test
```

**Structure Decision**: Single backend testing directory (`backend/tests/`) utilizing `pytest` fixture organization and `httpx.AsyncClient` with `ASGITransport(app=app)`.

## Complexity Tracking

*No constitution violations present. All architectural decisions align strictly with Principles I–VIII.*
