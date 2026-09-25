# Quickstart & Validation Guide: Database Schema & Migrations

**Feature Branch**: `001-db-schema-migrations` | **Date**: 2026-09-25

## Setup & Verification Steps

Follow these steps to execute Alembic schema migrations and populate initial seed data for the FrontRow ticketing platform.

### Prerequisites

- PostgreSQL database server running locally or via Docker
- Configured `.env` file in `backend/.env` with valid `DATABASE_URL` (e.g. `postgresql+asyncpg://postgres:postgres@localhost:5432/frontrow`)

---

### Step 1: Run Alembic Database Migrations

From the project root, execute the migration runner:

```bash
python scripts/run_migrations.py
```

Expected Output:
```text
Connecting to database configuration from backend/.env...
Running Alembic migration upgrade to 'head'...
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial_schema, Initial database schema creation
Database migrations applied successfully.
```

---

### Step 2: Verify Created Tables & Indexes

Verify table creation using PostgreSQL `psql` CLI:

```sql
-- List all tables
\dt

-- Expected tables:
-- users, events, seats, holds, orders, tickets, alembic_version

-- Verify indexes on seats and holds
\d seats
\d holds
```

Expected Indexes:
- `idx_seats_current_hold_id` on `seats(current_hold_id)`
- `idx_seats_event_id` on `seats(event_id)`
- `uq_seats_event_row_number` UNIQUE on `seats(event_id, row, seat_number)`
- `idx_holds_expires_at` on `holds(expires_at)`
- `idx_holds_order_id` on `holds(order_id)`

---

### Step 3: Populate Seed Event & Seat Grid

Execute the DML-only event seed script:

```bash
python scripts/seed_event.py
```

Expected Output:
```text
Connecting to database...
Inserting test user 'demo@frontrow.com'...
Inserting test event 'FrontRow Grand Concert'...
Populating 3x10 venue seat map (Rows A, B, C)...
Seeded 30 physical seat records (Row A: $150.00, Row B: $100.00, Row C: $50.00).
Seed operation completed successfully.
```

---

### Step 4: Verify Seed Data Queries

```sql
SELECT count(*) FROM seats WHERE status = 'AVAILABLE';
-- Expected count: 30

SELECT row, count(*), price FROM seats GROUP BY row, price ORDER BY row;
-- Expected output:
-- row | count | price
-------+-------+-------
-- A   |    10 | 150.00
-- B   |    10 | 100.00
-- C   |    10 |  50.00
```
