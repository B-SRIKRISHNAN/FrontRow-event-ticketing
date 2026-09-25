# Feature Specification: Database Schema & Migrations

**Feature Branch**: `001-db-schema-migrations`

**Created**: 2026-09-25

**Status**: Draft

**Input**: User description: "Spec 1 — Database Schema & Migrations: Table-by-table design: users, events, seats, holds, orders, tickets — types, constraints, indexes (especially seats.current_hold_id, holds.expires_at, holds.order_id). Alembic migration authoring for all tables (Principle VIII: exclusive migration authority, no raw DDL). Seed script (scripts/seed_event.py) — DML-only, POC 3x10 A/B/C grid per constitution section 5.x."

## Clarifications

### Session 2026-09-25

- Q: Which primary key generation strategy should be used across all database tables? → A: UUID for `holds.id` (`UUID` / `uuid4()`), and Auto-incrementing Integers (`BIGINT` / `Integer`) for `users`, `events`, `seats`, `orders`, and `tickets`. Matches Constitution and Blueprint requirements.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Relational Database Schema Creation (Priority: P1)

As a backend database developer, I want a complete PostgreSQL database schema defining `users`, `events`, `seats`, `holds`, `orders`, and `tickets` tables with strict constraints and indexes so that the high-concurrency seat locking and checkout engines operate on a consistent relational model.

**Why this priority**: Core relational foundation required before any backend API routes, authentication endpoints, or seat locking transactions can execute.

**Independent Test**: Can be tested by running the Alembic migration script via `python scripts/run_migrations.py` against a PostgreSQL database and verifying that all 6 tables, foreign keys, indexes, and constraints are created accurately.

**Acceptance Scenarios**:

1. **Given** a clean PostgreSQL database, **When** executing the migration runner, **Then** tables `users`, `events`, `seats`, `holds`, `orders`, and `tickets` are created.
2. **Given** the `seats` table, **When** inspecting indexes and constraints, **Then** `seats.current_hold_id` is indexed and a composite unique constraint exists on `(event_id, row, seat_number)`.
3. **Given** the `holds` table, **When** inspecting index definitions, **Then** `holds.expires_at` and `holds.order_id` are indexed to support ultra-fast expiry queries and reverse order lookups.

---

### User Story 2 - Exclusive Alembic Schema Authoring (Priority: P2)

As a database administrator, I want all DDL schema definitions and table creation steps packaged strictly inside version-controlled Alembic migration revisions under `backend/alembic/versions/` so that no dynamic or raw DDL queries exist in application code.

**Why this priority**: Enforces Constitution Principle VIII (Strict Alembic Migrations) across all database DDL lifecycle operations.

**Independent Test**: Can be tested by inspecting the Alembic migration directory (`backend/alembic/versions/`) to confirm revision files exist and executing `alembic upgrade head` and `alembic downgrade base` cleanly.

**Acceptance Scenarios**:

1. **Given** the `backend/alembic/versions/` directory, **When** inspecting revision files, **Then** an initial migration revision defines the complete DDL schema for all 6 tables.
2. **Given** database setup or tear-down, **When** executing migration upgrades and downgrades, **Then** schema migrations apply and roll back without errors.

---

### User Story 3 - Deterministic Event & Seat Grid Seeding (Priority: P3)

As a developer testing the system, I want a dedicated data seeding script (`scripts/seed_event.py`) that performs DML-only data insertions to populate a test event with a 3×10 venue seat grid (Rows A, B, C; Seats 1–10) across three price tiers so that API routes and frontend seat maps have initial seed data ready.

**Why this priority**: Provides the canonical POC dataset required for seat map rendering, seat search algorithms, and concurrency verification tests.

**Independent Test**: Can be tested by executing `python scripts/seed_event.py` post-migration, verifying 1 test event and 30 physical seat records (10 per row) are created with correct row-to-tier price mappings ($150 for Row A, $100 for Row B, $50 for Row C).

**Acceptance Scenarios**:

1. **Given** an updated database schema, **When** executing `python scripts/seed_event.py`, **Then** 30 seat rows (A1..A10, B1..B10, C1..C10) associated with a test event are inserted.
2. **Given** the seeded seats, **When** inspecting seat pricing and sections, **Then** Row A seats have `section = 'A'` and `price = 150.00`, Row B seats have `section = 'B'` and `price = 100.00`, and Row C seats have `section = 'C'` and `price = 50.00`.
3. **Given** the seed script, **When** inspecting SQL statements, **Then** the script executes DML (`INSERT`/`UPDATE`) operations exclusively and performs no DDL schema modifications per Constitution Principle VIII.

---

### Edge Cases

- What happens if the seed script is executed multiple times? The seed script must be idempotent (e.g. check for existing test event or use `ON CONFLICT DO NOTHING`) so re-running does not duplicate seats or fail with unique constraint violations.
- How are row-scoped seat numbers handled? `seat_number` resets to 1 for each row (Row A has 1..10, Row B has 1..10, Row C has 1..10). Global seat identity is derived solely from the primary key `id`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST define the `users` table schema containing `id` (primary key Integer autoincrement), `email` (unique string), `hashed_password` (string), and `created_at` (timestamp with timezone).
- **FR-002**: System MUST define the `events` table schema containing `id` (primary key Integer autoincrement), `title` (string), `description` (text, nullable), `venue_name` (string), `show_time` (timestamp with timezone), and `created_at` (timestamp with timezone).
- **FR-003**: System MUST define the `seats` table schema containing `id` (primary key Integer autoincrement), `event_id` (foreign key -> `events.id` Integer), `row` (string), `seat_number` (integer, row-scoped), `section` (string), `price` (decimal), `status` (string/enum: `'AVAILABLE'`, `'LOCKED'`, `'SOLD'`), and nullable `current_hold_id` (foreign key -> `holds.id` UUID).
- **FR-004**: System MUST define explicit indexes on `seats.current_hold_id`, `seats.event_id`, and a composite unique constraint on `(event_id, row, seat_number)`.
- **FR-005**: System MUST define the `holds` table schema containing `id` (primary key UUID `uuid4()`), `user_id` (foreign key -> `users.id` Integer), `event_id` (foreign key -> `events.id` Integer), `status` (string/enum: `'ACTIVE'`, `'COMPLETED'`, `'EXPIRED'`), `created_at` (timestamp with timezone), `expires_at` (timestamp with timezone), and nullable `order_id` (foreign key -> `orders.id` Integer).
- **FR-006**: System MUST define explicit indexes on `holds.expires_at` and `holds.order_id` to support fast lazy-read expiry filtering and reverse order-to-hold lookups.
- **FR-007**: System MUST define the `orders` table schema containing `id` (primary key Integer autoincrement), `user_id` (foreign key -> `users.id` Integer), `total_amount` (decimal), and `created_at` (timestamp with timezone). `orders` MUST NOT carry a `hold_id` column.
- **FR-008**: System MUST define the `tickets` table schema containing `id` (primary key Integer autoincrement), `order_id` (foreign key -> `orders.id` Integer), `seat_id` (foreign key -> `seats.id` Integer), `price_paid` (decimal), and `created_at` (timestamp with timezone).
- **FR-009**: System MUST package all DDL definitions inside Alembic migration revisions in `backend/alembic/versions/`, enforcing Constitution Principle VIII.
- **FR-010**: System MUST provide a DML-only seeding script in `scripts/seed_event.py` populating a 3×10 seat map across Rows A ($150), B ($100), and C ($50) matching Constitution Section 5.x.

### Key Entities

- **User (`users`)**: Authenticated buyer profile and order owner (Integer ID).
- **Event (`events`)**: Scheduled show metadata and venue details (Integer ID).
- **Seat (`seats`)**: Bookable unit with row, seat_number, status (`AVAILABLE`, `LOCKED`, `SOLD`), and pointer `current_hold_id` (Integer ID).
- **Hold (`holds`)**: 5-minute lease reservation tracking `user_id`, `event_id`, `expires_at`, `status`, and `order_id` (UUID ID).
- **Order (`orders`)**: Finalized transaction record post-checkout (Integer ID).
- **Ticket (`tickets`)**: Individual seat purchase confirmation item tied to an order (Integer ID).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of database tables (`users`, `events`, `seats`, `holds`, `orders`, `tickets`) and indexes are authored via Alembic migrations with zero raw DDL in application code.
- **SC-002**: Database migration upgrade (`alembic upgrade head`) and downgrade (`alembic downgrade base`) complete cleanly in under 5 seconds.
- **SC-003**: Executing `scripts/seed_event.py` inserts exactly 30 physical seat records across 3 price tiers without primary key or constraint conflicts.
- **SC-004**: Idempotent re-execution of `scripts/seed_event.py` succeeds without raising unique constraint violations or duplicating records.

## Assumptions

- PostgreSQL 14+ is used with `UUID` columns for `holds.id` and `seats.current_hold_id`, and `BIGINT` autoincrement for all other table primary keys.
- SQLAlchemy ORM models in `backend/app/models/` will mirror these exact table definitions in Spec 2.
