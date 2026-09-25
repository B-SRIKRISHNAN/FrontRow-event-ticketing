# Implementation Plan: Project Scaffolding & Tooling

**Branch**: `000-project-scaffolding` | **Date**: 2026-09-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/000-project-scaffolding/spec.md`

## Summary

Establish the top-level repository scaffolding, directory layout, isolated dependency management, environment secret templates, and database migration runner for the FrontRow event ticketing platform.

Technical approach:
1. Top-level layout per Constitution Section 8 (`frontend/`, `backend/`, `llm-engine/`, `scripts/`).
2. `uv`-managed Python projects for `backend/` and `llm-engine/` with separate `pyproject.toml` files ensuring distinct virtual environments.
3. Next.js App Router project initialized in `frontend/` using JavaScript (`.js` / `.jsx`).
4. Alembic migration initialization under `backend/alembic/` wired to SQLAlchemy asyncpg configuration.
5. Per-service `.env.example` templates enforcing Constitution Principle VII (Zero Secret Leakage).
6. Cross-platform Python migration helper script (`scripts/run_migrations.py`) enforcing Constitution Principle VIII.

## Technical Context

**Language/Version**: Python 3.11+ (for `backend/` and `llm-engine/`), Node.js 18+ / JavaScript (ES2022+ / JSX) for `frontend/`

**Primary Dependencies**:
- `backend/`: FastAPI, SQLAlchemy, asyncpg, Pydantic, Alembic, pytest, uv
- `llm-engine/`: FastAPI, Pydantic, google-genai, uv
- `frontend/`: React, Next.js (App Router)

**Storage**: PostgreSQL (asyncpg driver via SQLAlchemy ORM & Alembic migrations)

**Testing**: pytest (for Python services), pytest-asyncio, httpx

**Target Platform**: Linux / macOS / Windows developer environments

**Project Type**: Multi-service Web Application (Frontend + Backend API + LLM Microservice)

**Performance Goals**: Instant service setup (<30s initialization via `uv`), zero environment contamination

**Constraints**:
- Strict multi-service separation (no shared root Python virtualenv)
- Strict `.env.example` exclusivity (zero real credentials committed)
- Strict Alembic migration authority (no raw DDL in app code)

**Scale/Scope**: Initial repository setup & developer environment foundation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Absolute Concurrency & Double-Selling Immunity**: PASS — Scaffolding wires Alembic and SQLAlchemy async engine for `backend/`.
- **Principle II: Clean Architectural Separation**: PASS — Decouples `frontend/`, `backend/`, `llm-engine/`, and `scripts/` into independent service directories.
- **Principle III: Tri-Layer Lease Lifecycle Management**: PASS — Alembic migration setup will support `seats` and `holds` schemas.
- **Principle IV: Deterministic Candidate Seat Matching & AI Parsing**: PASS — Isolated `llm-engine/` service defined with Pydantic validation dependencies.
- **Principle V: Empirical Automated Concurrency Verification**: PASS — `pytest` + `pytest-asyncio` + `httpx` configured in `backend/` dependencies.
- **Principle VI: Mandatory Pydantic Validation & Type Safety**: PASS — `pydantic` installed as core dependency in `backend/` and `llm-engine/`.
- **Principle VII: Zero Secret Leakage & Environment Hygiene**: PASS — `.env.example` templates created for each service; `.gitignore` configured for `.env` files.
- **Principle VIII: Strict Alembic Migrations**: PASS — `backend/alembic/` initialized and `scripts/run_migrations.py` created.

**Gate Result**: PASSED — All constitutional gates satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/000-project-scaffolding/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical research & decisions
├── data-model.md        # Environment & service config data model
├── quickstart.md        # Environment validation quickstart guide
├── contracts/           # Environment & script contracts
│   └── env-contract.md  # Service environment contracts
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code Layout

```text
frontrow/
├── frontend/              # Next.js JavaScript web app (App Router)
│   ├── package.json
│   ├── next.config.js
│   └── .env.example
├── backend/               # Python FastAPI backend service
│   ├── pyproject.toml     # Managed by uv
│   ├── alembic/           # Database migration revisions & env.py
│   ├── alembic.ini
│   └── .env.example
├── llm-engine/            # Python FastAPI LLM microservice
│   ├── pyproject.toml     # Managed by uv
│   └── .env.example
├── scripts/               # Helper & operational scripts
│   └── run_migrations.py  # Cross-platform migration runner script
├── .gitignore             # Enforces secret exclusion & cache ignores
└── README.md              # Repository overview
```

**Structure Decision**: Option 2 (Web application with separate `frontend/`, `backend/`, `llm-engine/`, and `scripts/` directories).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
