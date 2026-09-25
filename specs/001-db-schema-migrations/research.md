# Technical Research & Decisions: Database Schema & Migrations

**Feature Branch**: `001-db-schema-migrations` | **Date**: 2026-09-25

## 1. Primary Key Type Mapping (UUID vs BigInteger)

- **Decision**: Use `UUID` (`uuid.uuid4()`) for `holds.id` and `seats.current_hold_id`, and `BIGINT` autoincrement primary keys for `users.id`, `events.id`, `seats.id`, `orders.id`, and `tickets.id`.
- **Rationale**: Directly aligns with Constitution Section 3, Blueprint Section 3, and explicit user clarification. `holds` requires un-guessable, globally unique UUID tokens (`hold_id`) generated at lease initiation. Entity tables (`users`, `events`, `seats`, `orders`, `tickets`) use standard integer primary keys for high-performance join efficiency and storage optimization.
- **Alternatives Considered**:
  - *UUID for All Tables*: Unnecessary storage footprint and index memory overhead for static entities like `users` and `seats`.

## 2. Foreign Key Cascade & Nullability Rules

- **Decision**:
  - `seats.current_hold_id`: Nullable foreign key -> `holds.id`. ON DELETE SET NULL. Nulled ONLY by the sweeper on lease expiration.
  - `holds.order_id`: Nullable foreign key -> `orders.id`. ON DELETE SET NULL. Set exactly once upon successful checkout.
  - `holds.user_id` / `holds.event_id`: NOT NULL foreign keys -> `users.id`, `events.id`. ON DELETE CASCADE.
  - `tickets.order_id` / `tickets.seat_id`: NOT NULL foreign keys -> `orders.id`, `seats.id`.
- **Rationale**: Guarantees relational integrity. `seats.current_hold_id` remains populated post-checkout as a permanent audit trail pointing to the hold that produced the sale.

## 3. High-Concurrency Index Strategy

- **Decision**: Create explicit indexes on:
  1. `seats.current_hold_id` (`idx_seats_current_hold_id`)
  2. `seats.event_id` (`idx_seats_event_id`)
  3. `seats` composite unique constraint: `uq_seats_event_row_number` on `(event_id, row, seat_number)`
  4. `holds.expires_at` (`idx_holds_expires_at`)
  5. `holds.order_id` (`idx_holds_order_id`)
- **Rationale**:
  - `idx_seats_current_hold_id` optimizes the `LEFT JOIN` between `seats` and `holds` during lock acquisition (Principle I).
  - `idx_holds_expires_at` optimizes lazy-read expiration filtering and the sweeper worker query (Principle III).
  - `idx_holds_order_id` optimizes reverse lookups from orders back to holds (`WHERE holds.order_id = :order_id`).

## 4. DML-Only Seeding Architecture (`scripts/seed_event.py`)

- **Decision**: Implement `scripts/seed_event.py` using Python `asyncpg` / `SQLAlchemy` async connection executing explicit `INSERT` statements with `ON CONFLICT DO NOTHING`.
- **Rationale**: Enforces Constitution Principle VIII (Strict Alembic Migrations). DDL schema creation is strictly isolated to Alembic migration scripts. Seeding performs idempotent data population without altering table structures.
