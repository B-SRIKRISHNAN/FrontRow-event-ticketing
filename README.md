# FrontRow — Event Ticketing Platform

> A multi-tier, real-time event ticketing platform built with Next.js 14, FastAPI, PostgreSQL, and Google Gemini LLM, featuring double-selling immunity and natural language AI seat selection.

---

## 🏛️ Architecture Overview

FrontRow implements a clean, 4-tier decoupled microservices architecture enforcing strict separation of concerns and security boundaries:

1. **Frontend Web App (Port 3000)**: Built with Next.js 14 App Router, React 18, and modern CSS design system. Renders interactive venue layout maps, seat hold timers, checkout, and AI search interface. Communicates exclusively with the Backend API via REST APIs.
2. **Backend API Microservice (Port 8000)**: Built with FastAPI, SQLAlchemy (asyncpg), Pydantic v2, and JWT authentication. Owns business logic, seat hold state machine, checkout, lease expiration sweeper, and atomic database transactions.
3. **LLM Engine Microservice (Port 8001)**: Built with FastAPI and Google Gemini API (`google-genai` SDK). Performs natural language semantic query parsing (extracting quantity, price budget, section preference, and seat adjacency rules) into strongly-typed Pydantic JSON models. Strictly read-only; has zero database connectivity and zero direct frontend connection.
4. **Database & Storage Layer (PostgreSQL 15+)**: Relational database with explicit ACID transaction boundaries, row-level locking (`SELECT ... FOR UPDATE OF seats NOWAIT`), and Alembic schema migrations (`backend/alembic/`).

```mermaid
graph TD
    Client["User Browser / Client"] <-->|HTTPS / REST| Frontend["Frontend App<br/>(Next.js 14 - :3000)"]
    Frontend <-->|REST APIs / JWT| Backend["Backend API<br/>(FastAPI - :8000)"]
    Backend <-->|SQL / asyncpg| Postgres[("PostgreSQL 15+<br/>(frontrow database)")]
    Backend <-->|REST / Pydantic DTOs| LLM["LLM Engine Microservice<br/>(FastAPI - :8001)"]
    LLM <-->|API Calls| Gemini["Google Gemini API<br/>(gemini-1.5-flash)"]

    classDef core fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef db fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff;
    classDef external fill:#581c87,stroke:#a855f7,stroke-width:2px,color:#fff;
    class Frontend,Backend,LLM core;
    class Postgres db;
    class Gemini external;
```

---

## 🛠️ Technology Stack

| Tier / Domain | Technologies & Libraries |
| :--- | :--- |
| **Frontend** | Node.js 18+, Next.js 14 (App Router), React 18, Vanilla CSS Design System |
| **Backend API** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (asyncpg), Alembic, Pydantic v2, PyJWT |
| **LLM Engine** | Python 3.11+, FastAPI, Google GenAI SDK (`google-genai`), Pydantic v2 |
| **Database** | PostgreSQL 15+ (Row-level `NOWAIT` locking, ACID transactions) |
| **Testing** | `pytest`, `pytest-asyncio`, `httpx` |
| **Orchestration**| Python cross-platform runner (`init.py`) & PowerShell wrapper (`init.ps1`) |

---

## 📂 Project Structure

```text
FrontRow-event-ticketing/
├── init.py                    # Cross-platform one-shot setup & runner script
├── init.ps1                   # Windows PowerShell entry point wrapper
├── README.md                  # Comprehensive documentation & Concurrency Design Note
├── backend/                   # Core Backend API Microservice (:8000)
│   ├── .env.example           # Backend environment template
│   ├── alembic/               # Alembic database schema migration scripts
│   ├── alembic.ini            # Alembic configuration
│   ├── app/
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── db/                # Async database engine & session pool
│   │   ├── models/            # SQLAlchemy ORM models (users, events, seats, holds, orders)
│   │   ├── schemas/           # Pydantic validation models & DTOs
│   │   ├── services/          # Business logic & seat locking engine
│   │   └── api/               # API route handlers (auth, events, holds, checkout)
│   └── tests/
│       ├── test_holds.py      # Hold lifecycle & lazy expiration tests
│       ├── test_orders.py     # Atomic checkout & payment tests
│       └── test_concurrency.py# 15-request concurrent collision test
├── llm-engine/                # LLM Microservice (:8001)
│   ├── .env.example           # LLM Engine environment template
│   └── app/
│       ├── main.py            # FastAPI entry point
│       └── services/          # Gemini natural language query parser
├── frontend/                  # Next.js 14 Frontend App (:3000)
│   ├── .env.example           # Frontend environment template
│   └── src/                   # React components, layout, and page routes
└── scripts/
    ├── run_migrations.py      # Alembic migration runner script
    └── seed_event.py          # DML event and seat grid seeder (30 seats)
```

---

## 🔑 Environment Configuration (`.env.example` Walkthrough)

FrontRow enforces a strict **Zero Secret Leakage** policy. Real `.env` files live inside their respective service directories (`backend/.env`, `llm-engine/.env`, `frontend/.env`), are ignored by git, and are automatically generated from `.env.example` templates during setup (`init.py` / `init.ps1`).

### 1. Backend Service (`backend/.env.example`)
| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/frontrow` | PostgreSQL database connection string using asyncpg driver |
| `JWT_SECRET` | `change-this-super-secret-key-in-production` | Secret key used to sign and verify JWT authentication tokens |
| `JWT_ALGORITHM` | `HS256` | HMAC signing algorithm for JWT tokens |
| `HOLD_DURATION_SECONDS` | `300` | Seat hold lease duration (default 5 minutes) |
| `LLM_ENGINE_URL` | `http://localhost:8001` | Backend API target URL for natural language LLM parsing |

### 2. LLM Engine Microservice (`llm-engine/.env.example`)
| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | `your_gemini_api_key_here` | Google Gemini API key for natural language seat search |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model selection for natural language search parsing |
| `LLM_PROVIDER` | `gemini` | Active LLM provider implementation (`gemini` or `mock`) |
| `PORT` | `8001` | Microservice HTTP server port |

### 3. Frontend Web App (`frontend/.env.example`)
| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Target Base URL for Backend REST API requests |

---

## ⚡ Quickstart & Setup Guide

### Prerequisites
- **Python**: 3.11+
- **Node.js**: 18+ (with `npm`)
- **PostgreSQL**: 15+ database running locally (or via Docker) with database `frontrow` created:
  ```bash
  createdb -U postgres frontrow
  ```

---

### Option A: One-Shot Automated Setup & Runner (Recommended)

1. **Configure Environment Files**:
   Before executing the runner, copy `.env.example` to `.env` in each service directory and configure your keys (e.g. `GEMINI_API_KEY` in `llm-engine/.env`):
   ```bash
   copy backend\.env.example backend\.env
   copy llm-engine\.env.example llm-engine\.env
   copy frontend\.env.example frontend\.env
   ```
   *(Note: `init.py` performs a strict pre-flight check to verify that all 3 `.env` files exist before running migrations or seeding, and will halt with an error if any required `.env` file is missing).*

2. **Execute Initialization Runner**:
   Run the setup script to execute database migrations, seed initial data, and automatically launch all 3 microservices in **3 dedicated, separate console windows**:

```powershell
# Cross-platform Python entry point
python init.py

# Or on Windows PowerShell
.\init.ps1
```

To run initialization without launching the microservice console windows:
```powershell
python init.py --skip-services
```

---

### Option B: Manual Step-by-Step Setup

If you prefer to setup each service manually:

1. **Environment Setup**:
   ```bash
   copy backend\.env.example backend\.env
   copy llm-engine\.env.example llm-engine\.env
   copy frontend\.env.example frontend\.env
   ```

2. **Database Migrations & Data Seeding**:
   ```bash
   python scripts/run_migrations.py
   python scripts/seed_event.py
   ```

3. **Launch Microservices (Separate Terminals)**:
   - **Backend API** (`:8000`):
     ```bash
     cd backend
     python -m uvicorn app.main:app --port 8000 --reload
     ```
   - **LLM Engine** (`:8001`):
     ```bash
     cd llm-engine
     python -m uvicorn app.main:app --port 8001 --reload
     ```
   - **Frontend Web App** (`:3000`):
     ```bash
     cd frontend
     npm run dev
     ```

---

## 🧪 Running Automated Tests

FrontRow maintains automated testing across backend API endpoints, concurrency collision mechanics, and frontend build verification.

### Track 1: Backend API Test Suite & Concurrency Proof

Execute backend unit and integration tests using `pytest`:

```bash
cd backend
pytest -v
```

To execute the standalone 15-request concurrent collision test:
```bash
python backend/tests/test_concurrency.py
```

### Track 2: Frontend Production Build Check

Verify Next.js compilation and type safety:

```bash
cd frontend
npm run build
```

---

## 🛡️ Concurrency Correctness — Design Note

### Double-Selling Immunity Guarantee

If two or more buyers attempt to hold or buy the exact same seat(s) at the exact same millisecond, **exactly one request succeeds and all others receive an immediate, non-blocking HTTP 409 Conflict rejection** — guaranteed zero double-holds and zero double-sells under heavy contention.

### 6-Step Proof of Correctness

1. **Single Source of Truth in Database**: The physical seat availability state lives exclusively on the PostgreSQL `seats` table (`status` column: `AVAILABLE`, `LOCKED`, `SOLD`), guarded strictly by PostgreSQL row-level locks.
2. **Instant Lock Manager Rejection (`SELECT ... FOR UPDATE OF seats NOWAIT`)**:
   Seat reservation queries use explicit PostgreSQL row locking with `NOWAIT`:
   ```sql
   SELECT seats.id, seats.status, holds.expires_at
   FROM seats
   LEFT JOIN holds ON seats.current_hold_id = holds.id
   WHERE seats.id IN (:seat_ids)
   FOR UPDATE OF seats NOWAIT;
   ```
   If another transaction holds a row lock on any target seat, PostgreSQL immediately aborts with error code `55P03` (`lock_not_available`). The backend catches `55P03` and returns an immediate HTTP `409 Conflict` without waiting or holding application threads.
3. **Atomic Transactional Availability Predicate**:
   The locking query's `WHERE` clause evaluates `seats.status = 'AVAILABLE' OR (seats.status = 'LOCKED' AND holds.expires_at < NOW())`. If the count of locked rows returned does not match the exact number of requested seats, the transaction instantly executes an all-or-nothing rollback and returns HTTP `409 Conflict`.
4. **Microsecond Physical Lock Duration**:
   Physical database row locks are held strictly inside explicit transaction blocks for ~2ms to 5ms. No physical locks or open connections are ever held while awaiting user interaction or external LLM service responses.
5. **Tri-Layer Redundant Lease Expiration**:
   Hold expiration (`expires_at` on `holds`) is enforced across 3 redundant layers:
   - *Lazy Expiration on Read*: `GET /events/{id}/seats` dynamically evaluates expired locked seats as `AVAILABLE` without write database locks.
   - *Lazy Overwrite on Lock*: Lock acquisition safely overwrites expired seat holds within the atomic transaction.
   - *Asynchronous Sweeper Worker*: A background worker running every 15s queries expired holds (`SKIP LOCKED`) and updates seats back to `AVAILABLE`.
6. **Atomic Conditional Checkout**:
   Checkout executes a mock payment stub, followed by an atomic SQL update:
   ```sql
   UPDATE seats
   SET status = 'SOLD'
   WHERE id IN (:seat_ids)
     AND current_hold_id = :provided_hold_id
     AND status = 'LOCKED';
   ```
   If 0 rows are updated (e.g. the hold expired or was reassigned before payment completed), the transaction rolls back, marks the hold expired, triggers a mock refund stub, and returns HTTP `409 Conflict`.

---

## 📊 Concurrency Collision Test Reproduction Guide

To empirically verify double-selling immunity on your local machine, execute the standalone collision test script:

```bash
python backend/tests/test_concurrency.py
```

### What the Test Executes
1. Resets target Seat ID 5 (Row A, Seat 5) to `AVAILABLE` status.
2. Generates 15 authenticated JWT user session tokens.
3. Clears dependency overrides to force real connection pool allocation (pool_size >= 15).
4. Fires 15 simultaneous HTTP `POST /api/v1/events/1/holds` requests targeting Seat ID 5 at the exact same millisecond via `asyncio.gather`.

### Expected Log Output

```text
================================================================================
                    FRONTROW CONCURRENCY COLLISION PROOF TEST                   
================================================================================
Target Seat ID      : 5
Initial Seat Status : AVAILABLE
Collision Scale     : 15 simultaneous HTTP requests
--------------------------------------------------------------------------------

[SETUP PHASE]
  - Target seat 5 reset to AVAILABLE status in PostgreSQL.
  - Generated 15 authenticated JWT user tokens.
  - Dependency overrides cleared to utilize real database connection pool (pool_size >= 15).

[DISPATCH PHASE]
  - Firing 15 concurrent POST /api/v1/events/1/holds requests via asyncio.gather...

[PER-REQUEST RESOLUTION PHASE]
  - [Req 00] -> HTTP 201 Created  | Winner Hold ID: 4a7c8912-3b4e-4f1a-8c90-123456789abc
  - [Req 01] -> HTTP 409 Conflict | Lock Contention Caught (Seat ID 5 is unavailable...)
  - [Req 02] -> HTTP 409 Conflict | Lock Contention Caught (Seat ID 5 is unavailable...)
  ...
  - [Req 14] -> HTTP 409 Conflict | Lock Contention Caught (Seat ID 5 is unavailable...)

================================================================================
                                SUMMARY RESULTS                                 
================================================================================
Total Collision Requests : 15
Execution Duration      : 45.12 ms
Successful Hold (201)    : 1 (Hold ID: 4a7c8912-3b4e-4f1a-8c90-123456789abc)
Lock Contention (409)    : 14 (Row lock unavailable / NOWAIT exception caught)
Post-Test Seat State     : LOCKED (current_hold_id = 4a7c8912-3b4e-4f1a-8c90-123456789abc)
Double-Selling Immunity  : VERIFIED (0 double-holds, 0 corrupted locks)
--------------------------------------------------------------------------------
[STATUS]: PASSED - Constitution Principle V Satisfied
================================================================================
```

---

## 📄 License & Attribution

FrontRow is developed as a production-grade demonstration of high-concurrency database locking, microservices separation, and AI natural language seat selection.
