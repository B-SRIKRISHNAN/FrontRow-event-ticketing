# Implementation Plan: Database Schema & Migrations

**Branch**: `001-db-schema-migrations` | **Date**: 2026-09-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-db-schema-migrations/spec.md`

## Summary

Design and author the initial database schema migration using Alembic (`backend/alembic/versions/`) defining all 6 core domain tables (`users`, `events`, `seats`, `holds`, `orders`, `tickets`), index definitions (`seats.current_hold_id`, `holds.expires_at`, `holds.order_id`), and create a DML-only event seed script (`scripts/seed_event.py`) populating the POC 3×10 venue seat map across three price tiers.

Technical approach:
1. Author single initial Alembic revision script in `backend/alembic/versions/001_initial_schema.py` introducing all 6 tables, foreign key relationships, and indexes.
2. Ensure strict ID type mapping: `holds.id` uses `UUID` (`uuid4()`), while `users.id`, `events.id`, `seats.id`, `orders.id`, and `tickets.id` use `BIGINT` autoincrement primary keys.
3. Configure composite unique constraint on `seats` (`event_id`, `row`, `seat_number`).
4. Implement DML-only seed script (`scripts/seed_event.py`) using asyncpg / SQLAlchemy async engine to populate 1 test event, 1 test user, and 30 physical seat units across Row A ($150), Row B ($100), and Row C ($50).

## Technical Context

**Language/Version**: Python 3.11+ (SQLAlchemy 2.0+ async engine, Alembic 1.13+, asyncpg driver)

**Primary Dependencies**: SQLAlchemy, Alembic, asyncpg, pydantic

**Storage**: PostgreSQL 14+ (UUID extension support / native UUID column type)

**Testing**: Alembic upgrade/downgrade execution tests (`python scripts/run_migrations.py`), seed script execution test (`python scripts/seed_event.py`)

**Target Platform**: Linux / macOS / Windows developer environments with PostgreSQL

**Project Type**: Database Schema & Migration Revision

**Performance Goals**: Migration upgrade execution <5s; fast indexed lookups on `holds.expires_at`, `holds.order_id`, and `seats.current_hold_id`

**Constraints**:
- Strict Alembic authority per Constitution Principle VIII (zero raw DDL in app/seed code)
- DML-only seeding in `scripts/seed_event.py` (no table creation in seed script)
- Idempotent seed execution (`ON CONFLICT` / existence check)

**Scale/Scope**: 6 tables, 30 seed seat units, POC multi-tier venue grid

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Absolute Concurrency & Double-Selling Immunity**: PASS — Schema indexes `seats.current_hold_id`, `holds.expires_at`, and `holds.order_id` to support `LEFT JOIN` and atomic checkout queries.
- **Principle II: Clean Architectural Separation**: PASS — Schema owned strictly by backend service.
- **Principle III: Tri-Layer Lease Lifecycle Management**: PASS — `holds.expires_at` defined as the sole source of truth for 5-minute lease expiry.
- **Principle IV: Deterministic Candidate Seat Matching & AI Parsing**: PASS — `seats` table defines `row`, `seat_number`, `section`, and `price` supporting `ORDER BY row ASC, seat_number ASC`.
- **Principle V: Empirical Automated Concurrency Verification**: PASS — Schema indexes support 10+ concurrent collision queries.
- **Principle VI: Mandatory Pydantic Validation & Type Safety**: PASS — Table column types mirror Pydantic domain models.
- **Principle VII: Zero Secret Leakage & Environment Hygiene**: PASS — Database credentials sourced strictly via `.env` / `DATABASE_URL`.
- **Principle VIII: Strict Alembic Migrations**: PASS — All DDL packaged inside `backend/alembic/versions/001_initial_schema.py`; seed script is DML-only.

**Gate Result**: PASSED — All constitutional gates satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-db-schema-migrations/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical research & DB schema decisions
├── data-model.md        # Relational schema DDL definitions
├── quickstart.md        # Database migration & seed validation guide
├── contracts/           # Database schema contracts
│   └── db-contract.md   # SQL DDL & table schema contract
└── checklists/
    ├── requirements.md  # Specification quality checklist
    └── setup.md         # Setup quality checklist
```

### Source Code Layout

```text
frontrow/
├── backend/
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py  # Initial database DDL migration revision
│   └── pyproject.toml
└── scripts/
    ├── run_migrations.py              # Cross-platform migration runner script
    └── seed_event.py                  # DML-only event & seat grid seed script
```

**Structure Decision**: Database schema and Alembic revision authored under `backend/alembic/versions/`; operational seed script under `scripts/seed_event.py`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
