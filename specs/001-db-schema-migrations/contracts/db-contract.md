# Interface Contract: Database Schema DDL & Seeding Specifications

**Feature Branch**: `001-db-schema-migrations` | **Date**: 2026-09-25

## 1. Alembic Migration Contract (`backend/alembic/versions/001_initial_schema.py`)

### Migration Identification

- **Revision ID**: `001_initial_schema`
- **Revises**: `None`
- **Create Date**: 2026-09-25

### Upgrade Actions (`upgrade()`)

1. Create `users` table (`id` BIGINT PK autoincrement, `email` VARCHAR UNIQUE, `hashed_password` VARCHAR, `created_at` TIMESTAMPTZ).
2. Create `events` table (`id` BIGINT PK autoincrement, `title` VARCHAR, `description` TEXT, `venue_name` VARCHAR, `show_time` TIMESTAMPTZ, `created_at` TIMESTAMPTZ).
3. Create `holds` table (`id` UUID PK default uuid4, `user_id` FK -> users.id, `event_id` FK -> events.id, `status` VARCHAR, `created_at` TIMESTAMPTZ, `expires_at` TIMESTAMPTZ, `order_id` FK -> orders.id).
4. Create `seats` table (`id` BIGINT PK autoincrement, `event_id` FK -> events.id, `row` VARCHAR, `seat_number` INT, `section` VARCHAR, `price` NUMERIC, `status` VARCHAR, `current_hold_id` FK -> holds.id).
5. Create `orders` table (`id` BIGINT PK autoincrement, `user_id` FK -> users.id, `total_amount` NUMERIC, `created_at` TIMESTAMPTZ).
6. Create `tickets` table (`id` BIGINT PK autoincrement, `order_id` FK -> orders.id, `seat_id` FK -> seats.id, `price_paid` NUMERIC, `created_at` TIMESTAMPTZ).
7. Create Indexes:
   - `idx_seats_current_hold_id` on `seats(current_hold_id)`
   - `idx_seats_event_id` on `seats(event_id)`
   - `uq_seats_event_row_number` UNIQUE on `seats(event_id, row, seat_number)`
   - `idx_holds_expires_at` on `holds(expires_at)`
   - `idx_holds_order_id` on `holds(order_id)`

### Downgrade Actions (`downgrade()`)

1. Drop tables in reverse dependency order (`tickets`, `orders`, `seats`, `holds`, `events`, `users`).

---

## 2. Seed Script CLI Contract (`scripts/seed_event.py`)

### Invocation Syntax

```bash
python scripts/seed_event.py [--backend-dir BACKEND_DIR]
```

### Contract Rules

1. Must execute **DML only** (`INSERT`/`UPDATE` via SQLAlchemy/asyncpg async connection).
2. Must verify database connection via `DATABASE_URL` from `backend/.env`.
3. Must insert 1 seed user (`demo@frontrow.com`).
4. Must insert 1 seed event ("FrontRow Grand Concert").
5. Must insert 30 seed seats:
   - Row A: seats 1..10, `section = 'A'`, `price = 150.00`
   - Row B: seats 1..10, `section = 'B'`, `price = 100.00`
   - Row C: seats 1..10, `section = 'C'`, `price = 50.00`
6. Must execute idempotently (`ON CONFLICT` or pre-check) returning exit code `0` on success.
