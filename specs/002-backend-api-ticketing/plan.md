# Implementation Plan: Core Backend API (Ticketing)

**Branch**: `002-backend-api-ticketing` | **Date**: 2026-09-25 | **Spec**: [`spec.md`](spec.md)

**Input**: Feature specification from [`specs/002-backend-api-ticketing/spec.md`](spec.md)

## Summary

Implement the core backend API microservice for FrontRow event ticketing in Python FastAPI. The service provides JWT authentication, event catalog browsing, real-time seat map querying (with 4s polling & lazy expiration), concurrency-safe seat hold acquisition (`LEFT JOIN`, `FOR UPDATE OF s NOWAIT`, raw SQL `text()`), explicit hold release, atomic checkout with mock payment & refund callbacks, order history, background lease sweeper worker (`SKIP LOCKED`), and AI search endpoint contract stubs.

---

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI 0.110+, Uvicorn 0.28+, SQLAlchemy 2.0+ (asyncio), asyncpg 0.29+, Pydantic 2.6+, greenlet 3.0+, python-jose 3.3+, passlib[bcrypt] 1.7+

**Storage**: PostgreSQL 14+ (managed via Alembic migrations)

**Testing**: `pytest`, `pytest-asyncio`, `httpx`

**Target Platform**: Linux server / Windows / macOS local development environment

**Project Type**: Web Service (FastAPI REST API)

**Performance Goals**: Sub-10ms row lock resolution during hold acquisition; sub-50ms seat map read latency under 4s client polling; 100% double-selling immunity under $\ge 10$ concurrent requests.

**Constraints**: Physical DB locks held $\le 5\text{ms}$; SQLAlchemy async connection pool sized to $\ge 15$ base connections + 10 overflow for requests; separate isolated pool (size 2) for background sweeper worker.

**Scale/Scope**: Single venue 3×10 seat map grid (Rows A, B, C; 30 seats total) for MVP.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Absolute Concurrency & Double-Selling Immunity**:
  - *Gate Status*: **PASS**. `POST /events/{id}/holds` uses `ORDER BY id ASC`, `LEFT JOIN`, `SELECT ... FOR UPDATE OF s NOWAIT` (raw SQL `text()`), non-blocking lock failure catch (`55P03` $\rightarrow$ 409 Conflict), and count validation rollback. Atomic checkout executes mock payment stub, conditional `SOLD` update, `COMPLETED`/`order_id` write, and mock refund on zero-row update failure.
- **Principle II: Clean Architectural Separation & Security Boundaries**:
  - *Gate Status*: **PASS**. User identity for all hold, release, checkout, and order operations is derived strictly from verified JWT claims (`sub`), never from client body/query params. Frontend ↔ Backend API ↔ PostgreSQL / LLM Engine separation strictly maintained.
- **Principle III: Tri-Layer Lease Lifecycle Management**:
  - *Gate Status*: **PASS**. `expires_at` lives exclusively on `holds`. Expiration enforced via lazy-expiry on read (`GET /events/{id}/seats`), lazy-overwrite on lock, and asynchronous sweeper worker (`SKIP LOCKED` every 15–30s). `seats.current_hold_id` is only nulled by sweeper/release.
- **Principle IV: Deterministic Candidate Seat Matching & AI Parsing Boundary**:
  - *Gate Status*: **PASS**. `POST /events/{id}/ai-search` shape and Pydantic schema validation defined. Candidate selection ordered by `row ASC, seat_number ASC`.
- **Principle V: Empirical Automated Concurrency Verification**:
  - *Gate Status*: **PASS**. Automated pytest concurrency suite (`tests/test_concurrency.py`) testing 10+ simultaneous requests targeting identical seats.
- **Principle VI: Mandatory Pydantic Schema & Type Safety**:
  - *Gate Status*: **PASS**. 100% of FastAPI endpoints enforce Pydantic request/response schemas.
- **Principle VII: Zero Secret Leakage**:
  - *Gate Status*: **PASS**. All secrets loaded via `.env`; `.env.example` contains placeholders only.
- **Principle VIII: Strict Alembic Schema Migrations**:
  - *Gate Status*: **PASS**. All DDL managed via Alembic migrations (`backend/alembic/versions/`); seed data uses DML only.

---

## Project Structure

### Documentation (this feature)

```text
specs/002-backend-api-ticketing/
├── plan.md              # Implementation plan
├── research.md          # Technical decisions & architecture research
├── data-model.md        # Entity ER diagram, DTOs & state transitions
├── quickstart.md        # Runnable setup & validation guide
└── contracts/           # API interface specifications
    └── api-contract.md  # OpenAPI REST endpoint specifications
```

### Source Code (repository root)

```text
backend/
├── alembic/
│   └── versions/
│       └── 001_initial_schema.py
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI application entrypoint & middleware
│   ├── config.py              # Environment settings & Pydantic BaseSettings
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py         # Primary & sweeper async engines & connection pools
│   ├── models/
│   │   ├── __init__.py
│   │   └── domain.py          # SQLAlchemy ORM models (User, Event, Seat, Hold, Order, Ticket)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── dto.py             # Pydantic request/response models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py        # JWT token issuance, password hashing & verification
│   │   └── dependencies.py    # Auth dependency (get_current_user from claims)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py          # Central APIRouter aggregation
│   │   └── v1/
│   │       ├── auth.py        # POST /auth/register, POST /auth/login
│   │       ├── events.py      # GET /events, GET /events/{id}/seats, POST /events/{id}/ai-search
│   │       ├── holds.py       # POST /events/{id}/holds, DELETE /holds/{hold_id}
│   │       ├── checkout.py    # POST /holds/{hold_id}/checkout
│   │       └── orders.py      # GET /orders
│   └── workers/
│       ├── __init__.py
│       └── sweeper.py         # Asynchronous background lease sweeper worker
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_events.py
│   ├── test_holds.py
│   ├── test_checkout.py
│   └── test_concurrency.py   # Concurrency collision suite (10+ simultaneous requests)
├── .env.example
├── pyproject.toml
└── README.md
```

**Structure Decision**: Single web application backend structure inside `backend/` adhering to 4-layer architectural separation.

---

## Complexity Tracking

*No Constitution Check violations. No entries required.*
