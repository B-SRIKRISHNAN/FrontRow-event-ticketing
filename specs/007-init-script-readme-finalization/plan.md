# Implementation Plan: Init Script & README Finalization

**Branch**: `007-init-script-readme-finalization` | **Date**: 2026-09-25 | **Spec**: [specs/007-init-script-readme-finalization/spec.md](file:///d:/projects/interviews/FrontRow-event-ticketing/specs/007-init-script-readme-finalization/spec.md)

**Input**: Feature specification from `/specs/007-init-script-readme-finalization/spec.md`

## Summary

The Init Script & README Finalization feature provides a one-shot initialization script (`init.py` / `init.ps1`) and a comprehensive, audit-ready `README.md` for the FrontRow ticketing platform. The one-shot init script automates setup by creating `.env` files from `.env.example` templates, executing Alembic database migrations via `scripts/run_migrations.py`, running the DML seed script (`scripts/seed_event.py`), and starting all three services (FastAPI Backend on `:8000`, LLM Engine on `:8001`, and Next.js Frontend on `:3000`). The `README.md` documents the system architecture, setup procedures, `.env.example` walkthrough, test execution commands, and a 6-step "Concurrency Correctness — Design Note" accompanied by reproduction steps for the 15-request concurrent collision test (`backend/tests/test_concurrency.py`).

## Technical Context

**Language/Version**: Python 3.11+ / PowerShell, Node.js 18+ (Next.js 14), Markdown

**Primary Dependencies**: `uv`, `pytest`, `fastapi`, `uvicorn`, `next`, `alembic`, `sqlalchemy`, `asyncpg`

**Storage**: PostgreSQL (`frontrow` database via `DATABASE_URL`)

**Testing**: `pytest` (unit, integration, and standalone `backend/tests/test_concurrency.py`), `npm run build`

**Target Platform**: Windows (PowerShell/cmd) & POSIX (Linux/macOS bash)

**Project Type**: One-Shot Subprocess Orchestration & Technical Documentation

**Performance Goals**: Init script complete in < 2 minutes; all 3 services responding in < 5 seconds; 15 concurrent collision requests completed in < 3 seconds

**Constraints**: Pure Python / PowerShell cross-platform script; zero real secrets committed; strict adherence to Principles I–VIII

**Scale/Scope**: 1 root `README.md`, 1 one-shot `init.py` / `init.ps1` script, 4 `.env.example` templates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Absolute Concurrency & Double-Selling Immunity)**: ✅ PASS. `README.md` includes the full 6-step Concurrency Correctness Design Note and reproduction steps for `backend/tests/test_concurrency.py`.
- **Principle II (Clean Architectural Separation & Security Boundaries)**: ✅ PASS. Architecture overview documents the 4 decoupled layers (Frontend ↔ Backend ↔ LLM Engine & PostgreSQL).
- **Principle III (Tri-Layer Lease Lifecycle Management)**: ✅ PASS. Documented in `README.md` architecture and setup guide.
- **Principle IV (Deterministic Candidate Seat Matching & AI Parsing Boundary)**: ✅ PASS. Documented in `README.md` system capabilities.
- **Principle V (Empirical Automated Concurrency Verification)**: ✅ PASS. Concurrency test execution and log-based proof output explicitly documented with command snippets.
- **Principle VI (Mandatory Schema Validation)**: ✅ PASS. Documented in architecture section.
- **Principle VII (Zero Secret Leakage)**: ✅ PASS. `.env.example` files documented with non-sensitive defaults; `.gitignore` enforced.
- **Principle VIII (Strict Alembic Migrations)**: ✅ PASS. Init script executes Alembic migrations via `scripts/run_migrations.py` and seeds data via `scripts/seed_event.py`.

## Project Structure

### Documentation (this feature)

```text
specs/007-init-script-readme-finalization/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── init_contracts.md# Init script & README interface contracts
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
FrontRow-event-ticketing/
├── README.md            # Comprehensive project documentation & Concurrency Design Note
├── init.py              # Cross-platform one-shot initialization and runner script
├── init.ps1             # PowerShell entry point wrapper for Windows
├── .env.example         # Root environment example template
├── backend/
│   ├── .env.example     # Backend API environment template
│   └── tests/
│       └── test_concurrency.py # Standalone 15-request collision test
├── llm-engine/
│   └── .env.example     # LLM Engine microservice environment template
├── frontend/
│   └── .env.example     # Frontend App environment template
└── scripts/
    ├── run_migrations.py# Alembic migration runner
    └── seed_event.py    # DML data seeder
```

**Structure Decision**: Cross-platform Python/PowerShell initialization script (`init.py` / `init.ps1`) and comprehensive root `README.md` at repository root.

## Complexity Tracking

*No constitution violations present. All architectural decisions align strictly with Principles I–VIII.*
