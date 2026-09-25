# Feature Specification: Project Scaffolding & Tooling

**Feature Branch**: `000-project-scaffolding`

**Created**: 2026-09-25

**Status**: Draft

**Input**: User description: "Spec 0 — Project Scaffolding & Tooling: Repo structure per constitution section 8 (frontend/, backend/, llm-engine/, scripts/, root docker-compose.yml optional). uv-managed Python projects for backend/ and llm-engine/ (separate pyproject.toml/lockfile each — independent services, not a shared monorepo Python env). Next.js app initialized in frontend/ (App Router). Alembic initialized under backend/alembic/, wired to the SQLAlchemy/asyncpg setup. Per-service .env.example files (Principle VII) — no real .env committed. Placeholder migration-runner script (scripts/run_migrations.py or shell equivalent, Principle VIII) — can be a stub until schema exists."

## Clarifications

### Session 2026-09-25

- Q: Which language / type system should be used for the Next.js App Router application in `frontend/`? → A: JavaScript (.js / .jsx) for standard plain JS setup without TypeScript compilation overhead.
- Q: How should the placeholder migration runner script in `scripts/` be implemented? → A: Python script (`scripts/run_migrations.py`) for cross-platform compatibility across Windows, Linux, and macOS.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Independent Microservice Environment Setup (Priority: P1)

As a developer building or running the project, I want completely decoupled directory structures and independent dependency management for the Backend API, LLM Engine, and Frontend application so that services can be developed, tested, and deployed autonomously without cross-service environment leakage or shared Python virtual environment conflicts.

**Why this priority**: Essential foundation required before any backend API routes, database schemas, or AI parsing features can be developed.

**Independent Test**: Can be fully verified by initializing each service directory (`backend/`, `llm-engine/`, `frontend/`), confirming `uv` manages separate Python dependencies for `backend/` and `llm-engine/` with distinct lockfiles, and confirming Next.js builds independently in `frontend/`.

**Acceptance Scenarios**:

1. **Given** a clean workspace, **When** examining the project layout, **Then** four primary directories exist (`frontend/`, `backend/`, `llm-engine/`, `scripts/`) matching Constitution Section 8.
2. **Given** the `backend/` and `llm-engine/` directories, **When** inspecting Python configuration, **Then** each service contains its own independent `pyproject.toml` file managed by `uv`, ensuring isolated virtual environments.
3. **Given** the `frontend/` directory, **When** inspecting web project structure, **Then** a Next.js App Router application structure using JavaScript (.js / .jsx) is present with its own package configuration.

---

### User Story 2 - Zero-Secret Configuration & Example Environments (Priority: P2)

As a security auditor and open-source maintainer, I want every service to provide a standardized `.env.example` file with documented variable names and safe placeholder values so that developers can configure local environments without committing real secrets, private keys, or API credentials to version control.

**Why this priority**: Enforces Constitution Principle VII (Zero Secret Leakage) from day one of project initialization.

**Independent Test**: Can be tested by verifying `.env.example` files exist in `frontend/`, `backend/`, and `llm-engine/`, and asserting that running `git status` or git secret scanners confirms zero `.env` or credential files are tracked in version control.

**Acceptance Scenarios**:

1. **Given** any service directory (`frontend/`, `backend/`, `llm-engine/`), **When** listing configuration files, **Then** a `.env.example` file is present containing required variable keys with safe placeholder values and explanatory comments.
2. **Given** local development environment creation, **When** a developer copies `.env.example` to `.env`, **Then** git ignores `.env` and `.env.local` files completely per `.gitignore`.

---

### User Story 3 - Database Migration Infrastructure (Priority: P3)

As a backend developer, I want Alembic database migration tooling and a dedicated local migration runner script established under `backend/alembic/` and `scripts/` so that all database schema changes can be authored, version-controlled, and executed consistently across local setup and automated environments.

**Why this priority**: Enforces Constitution Principle VIII (Strict Alembic Migrations) before any database models or migration revisions are written.

**Independent Test**: Can be tested by invoking the migration runner script (`scripts/run_migrations.py`), verifying it connects to the database configuration specified in `.env`, and executes Alembic migration commands cleanly.

**Acceptance Scenarios**:

1. **Given** the `backend/` service, **When** checking database tools, **Then** Alembic is configured with `backend/alembic/` directory and `alembic.ini` wired to SQLAlchemy asyncpg engine configuration.
2. **Given** the project root, **When** executing `python scripts/run_migrations.py`, **Then** the script executes Alembic migration upgrades cross-platform against the target database connection string.

---

### Edge Cases

- What happens if a developer attempts to install dependencies at the repository root? Root package installs should be avoided; `uv` and `npm` instructions must direct commands into `backend/`, `llm-engine/`, or `frontend/` subdirectories.
- How does the migration runner handle missing or unconfigured database connection variables? The script must provide clear error messages explaining missing `.env` variables instead of failing silently with raw traceback crashes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST establish the top-level repository structure containing `frontend/`, `backend/`, `llm-engine/`, and `scripts/` directories as defined in Constitution Section 8.
- **FR-002**: System MUST configure `backend/` as an independent Python project using `uv` with its own `pyproject.toml` and dependencies (`fastapi`, `sqlalchemy`, `asyncpg`, `pydantic`, `alembic`, `pytest`).
- **FR-003**: System MUST configure `llm-engine/` as an independent Python project using `uv` with its own `pyproject.toml` and dependencies (`fastapi`, `pydantic`, `google-genai`).
- **FR-004**: System MUST initialize `frontend/` as a React / Next.js application using JavaScript (.js / .jsx) with App Router structure and package configuration.
- **FR-005**: System MUST provide independent `.env.example` files in `frontend/`, `backend/`, and `llm-engine/` containing variable keys, safe placeholders, and explanatory comments, enforcing Constitution Principle VII.
- **FR-006**: System MUST initialize Alembic migration configuration under `backend/alembic/` and provide a cross-platform Python migration helper script (`scripts/run_migrations.py`) enforcing Constitution Principle VIII.

### Key Entities

- **Service Configuration**: Environment definition for each microservice (`DATABASE_URL`, `JWT_SECRET`, `LLM_ENGINE_URL`, `NEXT_PUBLIC_API_BASE_URL`).
- **Migration Pipeline**: Alembic revision environment and runner wrapper responsible for applying DDL migrations cleanly.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New developers can initialize virtual environments and install all dependencies across `backend/` and `llm-engine/` in under 30 seconds using `uv`.
- **SC-002**: 100% of environment variables required for service operation are documented in respective `.env.example` files with zero secret leaks.
- **SC-003**: Migration runner script (`scripts/run_migrations.py`) executes successfully with zero schema errors when invoked against a valid PostgreSQL database URL.
- **SC-004**: All 3 microservices (`frontend`, `backend`, `llm-engine`) can be started independently without inter-service virtual environment contamination.

## Assumptions

- Developers have Python 3.11+, `uv`, Node.js 18+, and PostgreSQL installed in their local development environment or container setup.
- Docker Compose setup is optional for MVP local development as individual services support standalone CLI execution.
