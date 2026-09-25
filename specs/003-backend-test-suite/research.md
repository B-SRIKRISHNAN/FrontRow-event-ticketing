# Technical Research: Backend Test Suite

**Feature Branch**: `003-backend-test-suite`
**Date**: 2026-09-25

## 1. Concurrency Proof Test Console Logging Design

### Problem Statement
Constitution Principle V requires empirical automated concurrency verification under a 10+ simultaneous collision scenario. Spec 3 mandates that `backend/tests/test_concurrency.py` must not merely pass assertion checks silently, but must produce a structured, reviewer-facing step-by-step console trace when run with `pytest -v -s`.

### Research Findings & Decision
- **Decision**: Implement a formatted console log output in `test_concurrency.py` structured into 4 distinct phases:
  1. **[SETUP PHASE]**: Log target seat ID, initial seat status (`AVAILABLE`), and count of generated test user identities.
  2. **[DISPATCH PHASE]**: Log the firing of 15 simultaneous HTTP `POST /api/v1/events/1/holds` requests via `asyncio.gather`, detailing request indices and launch timestamps.
  3. **[PER-REQUEST RESOLUTION PHASE]**: Iterate over responses and log each request index, HTTP status code (`201 Created` vs `409 Conflict`), response body payload, and execution time.
  4. **[SUMMARY BLOCK PHASE]**: Render a visually distinct summary banner detailing total requests, winning hold ID, rejected count, seat state post-collision, and explicit zero double-selling verification assertion.
- **Rationale**: Providing structured output directly in console logs makes `test_concurrency.py` self-documenting for technical reviewers evaluating lock contention, non-blocking `NOWAIT` behavior, and transaction isolation without needing to inspect raw assertions.

## 2. SQLAlchemy Connection Pool Sizing ($\ge 15$) Precondition Note

### Problem Statement
In async Python web applications, if the SQLAlchemy connection pool size (or `max_overflow`) is smaller than the number of incoming concurrent requests, requests queue at the connection pool acquire lock in Python application memory before ever reaching PostgreSQL's row-level lock manager (`SELECT FOR UPDATE NOWAIT`). This conceals database locking behavior and causes false timeouts.

### Research Findings & Decision
- **Decision**: Include explicit docstrings and warning comments at the top of `backend/tests/test_concurrency.py` documenting connection pool requirements:
  - `pool_size` $\ge 15$
  - `max_overflow` $\ge 10$
  - Clear `app.dependency_overrides` before launching `asyncio.gather` tasks so that incoming HTTP requests use the app's real database connection pool from `app.db.session` rather than sharing a single test fixture transaction.
- **Rationale**: Ensures that 15 concurrent HTTP requests instantiate 15 separate database connections running in parallel against PostgreSQL, accurately exercising Postgres's `55P03` (`lock_not_available`) engine path.

## 3. Test Track Separation Strategy (Unit vs Integration)

### Problem Statement
Test suites must balance execution speed with empirical fidelity. Fast unit tests validate schema definitions and logic without DB connections, while integration tests validate raw SQL locks, foreign key cascades, transaction rollbacks, and lease expirations against PostgreSQL.

### Research Findings & Decision
- **Decision**:
  - **Unit Track**: `backend/tests/test_auth.py` and standalone model/service tests run quickly with mocked DB or pure logic execution.
  - **Integration Track**: `backend/tests/test_events.py`, `backend/tests/test_holds.py`, `backend/tests/test_checkout.py`, `backend/tests/test_sweeper.py` run against a genuine PostgreSQL database with Alembic schema migrations applied.
  - **Concurrency Proof Track**: `backend/tests/test_concurrency.py` runs independently or alongside the integration suite.
- **Rationale**: Preserves rapid developer inner-loop testing while guaranteeing zero-mock integration proof for concurrency-critical domain flows.

## 4. Pytest Output Capture & Execution Configuration

### Problem Statement
Standard `pytest` output capture intercepts `stdout` and `stderr`, obscuring step-by-step console logs unless `-s` or `--capture=no` is explicitly passed.

### Research Findings & Decision
- **Decision**: Design `test_concurrency.py` console logs using standard `print()` statements formatted with clear headers and bullet points. Document execution commands using `pytest -v -s` in `quickstart.md` and `test_cli.md`.
- **Rationale**: `-s` disables output capture, allowing real-time streaming of setup, dispatch, per-request resolution, and summary block formatting to the reviewer's terminal.
