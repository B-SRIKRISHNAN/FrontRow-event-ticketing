# Test CLI Contract Specification: Backend Test Suite

**Feature Branch**: `003-backend-test-suite`
**Date**: 2026-09-25

## 1. Full Backend Test Suite Execution

### Command
```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

### Purpose
Executes all unit, integration, and concurrency tests in the `backend/tests/` directory.

### Inputs
- **Environment**: Active Python virtual environment with dependencies installed (`pytest`, `httpx`, `sqlalchemy`, `asyncpg`).
- **Database**: Running PostgreSQL database with Alembic migrations applied.

### Expected Output
- **Exit Code**: `0`
- **Output Stream**: Concise pass report listing test module names, test function names, execution times, and final summary (e.g. `8 passed in 13.01s`).

---

## 2. Standalone Concurrency Proof Test Execution

### Command
```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_concurrency.py -v -s
```

### Purpose
Executes the standalone, reviewer-facing 15-request collision proof test with uncaptured console output (`-s`), printing structured execution logs detailing setup, request dispatch, per-request resolution (HTTP `201` winner vs `409` conflict), and the final summary block.

### Inputs
- **Environment**: Active Python virtual environment.
- **Flags**: `-v` (verbose), `-s` (disable stdout capture).
- **Database**: Running PostgreSQL database with connection pool size $\ge 15$.

### Expected Output
- **Exit Code**: `0`
- **Output Stream**: Formatted step-by-step console logs with Setup Phase, Dispatch Phase, Per-Request Resolution Phase, and Summary Results block confirming 1 winner, 14 conflicts, zero double-selling, and `LOCKED` seat status.

---

## 3. Fast Unit Test Track Execution

### Command
```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_auth.py -v
```

### Purpose
Executes fast, isolated unit tests for JWT encoding/decoding, claims validation, password hashing, and Pydantic request schema validation.

### Inputs
- **Environment**: Active Python virtual environment.

### Expected Output
- **Exit Code**: `0`
- **Execution Time**: < 1.0s.

---

## 4. Integration Test Track Execution

### Command
```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_events.py tests/test_holds.py tests/test_checkout.py tests/test_sweeper.py -v
```

### Purpose
Executes end-to-end integration tests validating event seat maps, lazy expiration on read, hold creation, checkout with mock payment stub and refund rollback, and lease sweeper worker background recycling.

### Expected Output
- **Exit Code**: `0`
- **Execution Time**: < 10.0s.
