# Quickstart & Validation Guide: Core Backend API (Ticketing)

**Feature**: `002-backend-api-ticketing` | **Date**: 2026-09-25

## Setup & Verification Steps

Follow these steps to start the FastAPI core backend, run migrations/seeding, and validate API endpoints and concurrency locking.

### Prerequisites

- PostgreSQL database server running with Spec 1 migrations applied (`python scripts/run_migrations.py`)
- Seed data populated (`python scripts/seed_event.py`)
- Backend `.env` file configured with `DATABASE_URL` and `JWT_SECRET`

---

### Step 1: Start Core Backend API Server

From the project root directory:

```bash
cd backend
uv sync
uvicorn app.main:app --reload --port 8000
```

---

### Step 2: Validate Authentication Endpoints

```bash
# Register test user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "testbuyer@frontrow.com", "password": "Password123!"}'

# Login to retrieve JWT token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "testbuyer@frontrow.com", "password": "Password123!"}'
```

Expected Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "token_type": "bearer"
}
```

---

### Step 3: Inspect Event Seat Map & Lazy Expiry

```bash
curl -X GET http://localhost:8000/events/1/seats
```

Expected Output:
- 30 seats returned with prices ($150, $100, $50) and status `AVAILABLE`.

---

### Step 4: Validate Hold Acquisition & Concurrency Locking

```bash
# Acquire hold for seats 1 & 2
curl -X POST http://localhost:8000/events/1/holds \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"seat_ids": [1, 2]}'
```

Expected Output:
- HTTP `201 Created` with `hold_id` UUID and 5-minute `expires_at`.

---

### Step 5: Validate Atomic Checkout

```bash
curl -X POST http://localhost:8000/holds/<HOLD_UUID>/checkout \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"payment_token": "mock_token_ok"}'
```

Expected Output:
- HTTP `200 OK` returning created order details with tickets.

---

### Step 6: Verify Concurrency Immunity Suite

```bash
cd backend
pytest tests/test_concurrency.py -v
```
