# FrontRow — Seat-Level Event Ticketing Platform

FrontRow is a seat-level event ticketing platform engineered to guarantee absolute correctness and double-selling immunity under high concurrency. The system enables users to view real-time seat states, temporarily lock seats for a checkout window, and purchase them safely. It includes an isolated, read-only LLM assistant microservice that parses natural language queries into structured preferences.

---

## Architecture Overview

FrontRow enforces clean architectural separation across four distinct top-level directories:

* **`frontend/`**: React / Next.js web application (App Router, JavaScript) providing seat map visualization, countdown timers, checkout flows, and AI search input.
* **`backend/`**: Python FastAPI core application managing authentication (JWT), seat maps, hold lifecycles, atomic concurrency locks, checkout transactions, and order history.
* **`llm-engine/`**: Isolated Python FastAPI microservice wrapping an abstracted LLM provider interface (default: Gemini) with Pydantic response validation.
* **`scripts/`**: Operational helper scripts including cross-platform database migration runners (`run_migrations.py`) and seed scripts.

---

## Repository Setup & Tooling

### Prerequisites

- Python 3.11+
- `uv` package manager (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Node.js 18+ and `npm`
- PostgreSQL 14+

---

## Quickstart & Environment Setup

### 1. Configure Environment Secrets

Each microservice maintains its own independent `.env.example` template:

```bash
# Copy example configuration templates to active .env files
cp backend/.env.example backend/.env
cp llm-engine/.env.example llm-engine/.env
cp frontend/.env.example frontend/.env
```

> **Note**: Active `.env` files are strictly excluded from version control per Constitution Principle VII.

---

### 2. Initialize Microservice Dependencies

#### Backend Service (`backend/`)
```bash
cd backend
uv sync
```

#### LLM Engine Service (`llm-engine/`)
```bash
cd ../llm-engine
uv sync
```

#### Frontend Application (`frontend/`)
```bash
cd ../frontend
npm install
```

---

### 3. Database Migrations & Seeding

Database schema changes are managed exclusively via Alembic (`backend/alembic/`) per Constitution Principle VIII. Execute the cross-platform migration runner to apply DDL:

```bash
python scripts/run_migrations.py
```

To roll back migrations to base:
```bash
python scripts/run_migrations.py --revision base
```

To populate the deterministic seed user (`demo@frontrow.com`), seed event ("FrontRow Grand Concert"), and 30 physical seat records (Rows A: $150, B: $100, C: $50), execute the DML seed script:

```bash
python scripts/seed_event.py
```

---

## Verification & Testing

### Concurrency Collision Verification

Automated concurrency test scripts test 10+ simultaneous requests targeting the exact same available seat at the same millisecond:

```bash
cd backend
pytest tests/test_concurrency.py -v
```

---

## License

FrontRow is licensed under the MIT License.
