# Technical Research & Decisions: Project Scaffolding & Tooling

**Feature Branch**: `000-project-scaffolding` | **Date**: 2026-09-25

## 1. Python Package & Environment Management (`uv`)

- **Decision**: Use `uv` to manage isolated Python virtual environments independently in `backend/` and `llm-engine/`.
- **Rationale**: `uv` is extremely fast (10-100x faster than standard `pip`), provides deterministic lockfiles (`uv.lock`), and cleanly manages per-directory virtual environments (`.venv/` within each service directory) without polluting the root repository or requiring complex monorepo workspace configurations.
- **Alternatives Considered**:
  - *Standard `pip` + `venv`*: Slower dependency resolution, manual virtualenv activation required, lacks lockfile pinning out of the box.
  - *Poetry*: Heavy dependency management overhead, slower lock generation compared to `uv`.

## 2. Frontend Framework & Language Choice (Next.js + JavaScript)

- **Decision**: Initialize `frontend/` as a Next.js App Router project using JavaScript (`.js` / `.jsx`).
- **Rationale**: Next.js App Router provides built-in server/client component rendering, file-system routing, and simple integration with React state hooks. Plain JavaScript eliminates TypeScript compilation overhead and aligns with the user's explicit preference.
- **Alternatives Considered**:
  - *TypeScript*: Rejected based on explicit user decision during `/speckit-clarify`.
  - *Vite + React SPA*: Lacks server-side rendering support and built-in routing conventions out of the box.

## 3. Database Migration Framework (Alembic + SQLAlchemy `asyncpg`)

- **Decision**: Use Alembic initialized under `backend/alembic/` configured to import SQLAlchemy models and connect via `asyncpg`.
- **Rationale**: Enforces Constitution Principle VIII (Strict Alembic Migrations). `asyncpg` is the fastest PostgreSQL driver for Python asyncio applications, and Alembic provides version-controlled migration scripts for reliable schema evolution.
- **Alternatives Considered**:
  - *Raw DDL Scripts*: Strictly forbidden by Constitution Principle VIII due to lack of rollback tracking and automated versioning.

## 4. Migration Runner Script (`scripts/run_migrations.py`)

- **Decision**: Create a cross-platform Python script (`scripts/run_migrations.py`) to execute Alembic migrations programmatically.
- **Rationale**: Works natively on Windows, Linux, and macOS without requiring Bash shell environments. It imports Alembic configuration or invokes Alembic CLI programmatically, verifying `.env` database connection strings before running migrations.
- **Alternatives Considered**:
  - *POSIX Shell Script (`run_migrations.sh`)*: Requires Bash environment on Windows, causing compatibility issues for Windows developers.

## 5. Secret Management & `.env.example` Hygiene

- **Decision**: Provide explicit `.env.example` templates in `frontend/`, `backend/`, and `llm-engine/` while strictly ignoring active `.env` files in `.gitignore`.
- **Rationale**: Directly enforces Constitution Principle VII (Zero Secret Leakage). Ensures developers can clone the repository and configure local environments safely.
- **Alternatives Considered**:
  - *Root `.env` file*: Rejected per Constitution Section 8 — each service must own its independent environment configuration to support standalone containerization or execution.
