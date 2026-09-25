# Tasks: Database Schema & Migrations

**Input**: Design documents from `specs/001-db-schema-migrations/`

**Prerequisites**: `plan.md` (required), `spec.md` (required), `data-model.md`, `contracts/db-contract.md`, `quickstart.md`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Alembic versions directory setup and migration infrastructure readiness.

- [x] T001 Verify Alembic versions directory structure `backend/alembic/versions/` and configuration file `backend/alembic.ini`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend database model package structure prior to schema revision authoring.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T002 Create backend database package placeholders in `backend/app/models/__init__.py` and `backend/app/db/__init__.py`

**Checkpoint**: Foundational package structure ready — user story migration authoring can now begin.

---

## Phase 3: User Story 1 - Relational Database Schema Creation (Priority: P1) 🎯 MVP

**Goal**: Complete PostgreSQL DDL schema definition across all 6 core domain tables with strict foreign key constraints and indexes.

**Independent Test**: Execute `python scripts/run_migrations.py` against PostgreSQL verifying tables `users`, `events`, `seats`, `holds`, `orders`, and `tickets` are created.

- [x] T003 [P] [US1] Define `users` and `events` table DDL schemas in `backend/alembic/versions/001_initial_schema.py`
- [x] T004 [P] [US1] Define `holds` table DDL schema with UUID primary key and index `idx_holds_expires_at` in `backend/alembic/versions/001_initial_schema.py`
- [x] T005 [P] [US1] Define `seats` table DDL schema with foreign key `current_hold_id`, index `idx_seats_current_hold_id`, and composite unique constraint `uq_seats_event_row_number` in `backend/alembic/versions/001_initial_schema.py`
- [x] T006 [P] [US1] Define `orders` and `tickets` table DDL schemas with index `idx_holds_order_id` in `backend/alembic/versions/001_initial_schema.py`
- [x] T007 [US1] Complete initial Alembic migration revision script in `backend/alembic/versions/001_initial_schema.py` with full `upgrade()` and `downgrade()` functions per contract `specs/001-db-schema-migrations/contracts/db-contract.md`

**Checkpoint**: At this point, User Story 1 (Alembic DDL migration) is fully functional and testable.

---

## Phase 4: User Story 2 - Exclusive Alembic Schema Authoring (Priority: P2)

**Goal**: Package all DDL exclusively inside Alembic migrations under `backend/alembic/versions/` enforcing Constitution Principle VIII.

**Independent Test**: Verify `alembic upgrade head` and `alembic downgrade base` execute cleanly without raw DDL in application code.

- [x] T008 [US2] Verify Alembic migration execution (`upgrade head` and `downgrade base`) via `scripts/run_migrations.py`
- [x] T009 [US2] Ensure zero raw DDL statements exist in application code or seed scripts, enforcing Constitution Principle VIII

**Checkpoint**: User Stories 1 AND 2 are fully compliant with Constitution Principle VIII.

---

## Phase 5: User Story 3 - Deterministic Event & Seat Grid Seeding (Priority: P3)

**Goal**: Implement DML-only seed script (`scripts/seed_event.py`) populating 1 test user, 1 test event, and 30 physical seat units across 3 price tiers.

**Independent Test**: Execute `python scripts/seed_event.py` post-migration verifying 30 physical seat records inserted across Rows A ($150), B ($100), and C ($50).

- [x] T010 [US3] Create DML-only event seeding script in `scripts/seed_event.py` using SQLAlchemy async engine / asyncpg connection
- [x] T011 [US3] Implement idempotent insertion of 1 test user (`demo@frontrow.com`) and 1 test event ("FrontRow Grand Concert") in `scripts/seed_event.py`
- [x] T012 [US3] Implement idempotent 3×10 seat grid population in `scripts/seed_event.py` for Rows A ($150.00), B ($100.00), and C ($50.00) matching Constitution Section 5.x
- [x] T013 [US3] Test executing `python scripts/seed_event.py` verifying 30 physical seat records are inserted without constraint errors

**Checkpoint**: All 3 user stories are independently functional, seeded, and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation updates and quickstart validation.

- [x] T014 [P] Update `README.md` database section with migration and seed execution instructions
- [x] T015 Run quickstart validation guide in `specs/001-db-schema-migrations/quickstart.md` to verify database schema and seed data

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories.
- **User Stories (Phases 3–5)**: All depend on Foundational phase completion.
  - Can proceed sequentially in priority order (US1 → US2 → US3).
- **Polish (Phase 6)**: Depends on User Stories 1–3 being complete.

### Parallel Opportunities

- **Phase 3 (US1)**: T003, T004, T005, and T006 (table schema definitions) can be drafted in parallel before consolidating in T007.
- **Phase 5 (US3)**: T011 and T012 can be implemented in parallel inside `scripts/seed_event.py`.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002)
3. Complete Phase 3: User Story 1 (T003, T004, T005, T006, T007)
4. **VALIDATE**: Run `python scripts/run_migrations.py` to create PostgreSQL schema.

### Incremental Delivery

1. Setup + Foundational → Migration directory ready.
2. User Story 1 → DDL schema revision `001_initial_schema.py` (MVP!).
3. User Story 2 → Migration upgrade/downgrade validation.
4. User Story 3 → DML seed script `scripts/seed_event.py` (3×10 seat grid).
5. Polish → `README.md` update and `quickstart.md` verification pass.
