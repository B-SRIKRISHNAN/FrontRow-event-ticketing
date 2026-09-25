# Interface Contracts: Init Script & README Finalization

**Feature Branch**: `007-init-script-readme-finalization`
**Date**: 2026-09-25

## 1. One-Shot Init Script CLI Interface

### Command Invocation

```powershell
# Cross-platform Python runner
python init.py [--skip-env] [--skip-migrations] [--skip-seed] [--skip-services]

# PowerShell entry wrapper (Windows)
.\init.ps1
```

### Execution Steps & Exit Codes

| Step | Action | Success Indicator | Error Handling |
| :--- | :--- | :--- | :--- |
| **1. Env File Copy** | Copies `.env.example` -> `.env` if missing | `.env` file exists | Skips if `.env` exists |
| **2. Migrations** | Runs `python scripts/run_migrations.py` | Exit code 0 | Halts initialization |
| **3. DML Seeding** | Runs `python scripts/seed_event.py` | Exit code 0 | Halts initialization |
| **4. Services** | Spawns Backend (`:8000`), LLM (`:8001`), Frontend (`:3000`) | Processes active | Press Ctrl+C to terminate |

---

## 2. Concurrency Test Execution Contract

### Command Invocation

```powershell
# Run standalone 15-request concurrent collision proof test
python backend/tests/test_concurrency.py
```

### Expected Log Output Structure

```text
=== CONCURRENCY COLLISION TEST INITIALIZED ===
Target Seat ID: 1 (Row A, Seat 1) | Concurrent Requests: 15
Firing 15 simultaneous hold requests...

[REQ-01] Status: 200 OK | Hold ID: 4a7c... | Elapsed: 42ms
[REQ-02] Status: 409 Conflict | Detail: Seat ID 1 is unavailable...
[REQ-03] Status: 409 Conflict | Detail: Seat ID 1 is unavailable...
...
[REQ-15] Status: 409 Conflict | Detail: Seat ID 1 is unavailable...

=== TEST RESULTS VERIFIED ===
Total Requests: 15
Successful Holds (200 OK): 1
Conflict Rejections (409 Conflict): 14
Database Integrity: 1 active hold record, 0 double-holds.
TEST PASSED.
```
