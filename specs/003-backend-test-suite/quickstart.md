# Quickstart & Validation Guide: Backend Test Suite

**Feature Branch**: `003-backend-test-suite`
**Date**: 2026-09-25

This guide provides runnable validation commands to verify all tracks of the FrontRow backend test suite, including fast unit tests, real-database integration tests, and the reviewer-facing standalone concurrency proof test.

---

## Prerequisites

1. **Working Directory**: Ensure shell working directory is set to `backend/`:
   ```powershell
   cd d:\projects\interviews\FrontRow-event-ticketing\backend
   ```
2. **Database Engine**: Ensure PostgreSQL database server is running locally on port 5432 and migrations have been executed:
   ```powershell
   .\.venv\Scripts\python.exe -m alembic upgrade head
   ```
3. **Environment Setup**: Ensure `backend/.env` is configured with `ASYNC_DATABASE_URL` pointing to PostgreSQL with `pool_size=15` and `max_overflow=10`.

---

## Validation Scenario 1: Standalone Reviewer-Facing Concurrency Proof

Execute the standalone concurrency proof test with stdout logging enabled to inspect the step-by-step 15-request collision trace:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_concurrency.py -v -s
```

### Expected Console Output
```text
================================================================================
                    FRONTROW CONCURRENCY COLLISION PROOF TEST                   
================================================================================
Target Seat ID      : 5
Initial Seat Status : AVAILABLE
Collision Scale     : 15 simultaneous HTTP requests

[SETUP PHASE]
  - Reset seat ID 5 to AVAILABLE status in PostgreSQL.
  - Generated 15 authenticated JWT user tokens.
  - Reset app dependency overrides to utilize real connection pool (pool_size >= 15).

[DISPATCH PHASE]
  - Firing 15 concurrent POST /api/v1/events/1/holds requests via asyncio.gather...

[PER-REQUEST RESOLUTION PHASE]
  - [Req 00] -> HTTP 409 Conflict | Body: {"detail":"Seat row locking failed or contention detected"}
  - [Req 01] -> HTTP 201 Created  | Hold ID: ...
  ...
  - [Req 14] -> HTTP 409 Conflict | Body: {"detail":"Seat row locking failed or contention detected"}

================================================================================
                                SUMMARY RESULTS                                 
================================================================================
Total Collision Requests : 15
Successful Hold (201)    : 1
Lock Contention (409)    : 14
Double-Selling Immunity  : VERIFIED (0 double-holds, 0 invalid statuses)
Post-Test Seat State     : LOCKED
--------------------------------------------------------------------------------
[STATUS]: PASSED - Constitution Principle V Satisfied
================================================================================
PASSED tests/test_concurrency.py::test_concurrency_collision_exact_one_winner
```

---

## Validation Scenario 2: Full Backend Test Suite

Execute the entire backend test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

### Expected Outcome
- All tests across `test_auth.py`, `test_events.py`, `test_holds.py`, `test_checkout.py`, `test_sweeper.py`, and `test_concurrency.py` pass cleanly.
- Execution time: < 20 seconds.

---

## Validation Scenario 3: Fast Unit Test Track

Execute the isolated unit test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_auth.py -v
```

### Expected Outcome
- Fast verification of JWT claims encoding, decoding, expiration handling, and password hashing logic.
- Execution time: < 1.0 second.

---

## Validation Scenario 4: Real-Database Integration Track

Execute all database integration test modules:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_events.py tests/test_holds.py tests/test_checkout.py tests/test_sweeper.py -v
```

### Expected Outcome
- Full integration coverage validating lazy expiration on read, atomic hold acquisition, checkout payment/refund stubs, and background sweeper recycling.
- Execution time: < 10.0 seconds.
