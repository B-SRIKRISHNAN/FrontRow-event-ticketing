# Feature Specification: Init Script & README Finalization

**Feature Branch**: `007-init-script-readme-finalization`

**Created**: 2026-09-25

**Status**: Draft

**Input**: User description: "Spec 7 — Init Script & README Finalization: One-shot script: create real .env files from examples (or prompt for values), run Alembic migrations via the runner script, run seed script, start all three services; README: architecture summary, setup steps, .env.example walkthrough, how to run tests (both tracks, noting the concurrency test's standalone invocation and its log-based proof output), reproduction steps for the concurrency test specifically; Also include a brief note on how our concurrency logic is valid and prevents two people booking the same seat(s) (6-step Concurrency Correctness Design Note)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One-Shot Automated Environment & Services Initialization (Priority: P1) 🎯 MVP

As a developer or evaluator, I want to execute a single one-shot initialization command so that environment files (`.env`) are auto-created from templates, database migrations and DML seeding are executed, and all three services (Backend API, LLM Engine, Frontend) are started automatically.

**Why this priority**: Streamlines onboarding and demonstration by eliminating manual step-by-step setup commands across 3 separate microservice directories.

**Independent Test**: Can be tested independently by running the one-shot init script on a fresh clone and verifying that `.env` files exist, database migrations/seeds succeed, and all 3 services respond on ports 8000, 8001, and 3000.

**Acceptance Scenarios**:

1. **Given** a fresh clone without `.env` files, **When** the developer runs the init script, **Then** the script creates real `.env` files from `.env.example` templates across root, `backend/`, `llm-engine/`, and `frontend/`.
2. **Given** created `.env` files, **When** the init script executes, **Then** it runs Alembic migrations (`python scripts/run_migrations.py`), executes DML data seeding (`python scripts/seed_event.py`), and reports successful database population.
3. **Given** database setup complete, **When** the init script finishes initialization, **Then** it launches the Backend API (`:8000`), LLM Engine (`:8001`), and Frontend App (`:3000`) concurrently.

---

### User Story 2 - Comprehensive Project Architecture & Setup Documentation (Priority: P1) 🎯 MVP

As a developer or reviewer, I want to read a comprehensive `README.md` at the repository root so that I understand the multi-tier architecture, environment variable requirements, execution options, and test suite commands.

**Why this priority**: Essential for project evaluators and open-source contributors to understand system structure and setup procedures.

**Independent Test**: Can be tested independently by following the `README.md` instructions step-by-step on a clean environment and asserting all build, test, and run commands complete cleanly.

**Acceptance Scenarios**:

1. **Given** a new reader opening the repository, **When** they read `README.md`, **Then** they find an executive architectural summary, technology stack choices (Next.js 14, FastAPI, PostgreSQL, Gemini LLM), and clear directory structure layout.
2. **Given** a developer configuring environment variables, **When** reviewing `README.md`, **Then** they see a complete `.env.example` walkthrough explaining each environment variable's purpose, default values, and production overrides.
3. **Given** a tester running automated tests, **When** following `README.md`, **Then** they find exact commands for running backend unit/integration tests (`pytest`) and frontend build checks (`npm run build`).

---

### User Story 3 - Concurrency Correctness Proof & Test Reproduction Guide (Priority: P2)

As a technical auditor or architect, I want to read an explicit "Concurrency Correctness — Design Note" and run the 15-request collision test script in `README.md` so that I can empirically observe log-based proof that zero double-holds and zero double-sells occur under heavy contention.

**Why this priority**: Empirically proves Constitution Principle I compliance and validates double-selling immunity.

**Independent Test**: Can be tested independently by executing `python backend/tests/test_concurrency.py` as documented in `README.md` and observing 1 successful hold alongside 14 immediate `409 Conflict` responses.

**Acceptance Scenarios**:

1. **Given** an architect reviewing system design, **When** reading the Concurrency Design Note in `README.md`, **Then** they see a detailed 6-step breakdown of row-level PostgreSQL locking (`FOR UPDATE OF seats NOWAIT`), single-transaction availability predicates, short lock duration, redundant lease expiration, and conditional checkout safeguards.
2. **Given** an auditor validating concurrency, **When** they execute the documented concurrency test command (`python backend/tests/test_concurrency.py`), **Then** 15 simultaneous hold requests fire concurrently at the exact same seat, outputting detailed dispatch logs showing 1 `200 OK` winner and 14 `409 Conflict` losers with zero database double-holds.

---

### Edge Cases

- What happens if PostgreSQL is not running when the init script runs? The script displays a clear error message indicating database connection failure and instructions to verify PostgreSQL service status.
- What happens if ports 8000, 8001, or 3000 are already in use? The init script detects port conflicts and reports which port is bound before exiting cleanly.
- What happens if `.env` files already exist? The init script preserves existing `.env` files and prompts/skips overwriting to protect user configuration.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an automated one-shot initialization script (`init.py` or `init.ps1`) that creates real `.env` files from `.env.example` templates, runs Alembic migrations, seeds deterministic demo data, and starts all 3 services.
- **FR-002**: System MUST provide a comprehensive `README.md` containing architectural overview, tech stack breakdown, setup walkthrough, `.env` variable reference, and test suite instructions.
- **FR-003**: `README.md` MUST include a dedicated "Concurrency Correctness — Design Note" section detailing the 6-step proof of double-selling immunity (PostgreSQL row locking, `NOWAIT` lock manager rejection, single-transaction atomic predicates, short lock duration, redundant lease expiration, and atomic checkout safeguards).
- **FR-004**: `README.md` MUST provide step-by-step reproduction instructions for running the 15-request concurrent collision test (`python backend/tests/test_concurrency.py`) and interpreting its log-based proof output.

### Key Entities *(include if feature involves data)*

- **Initialization Script Config**: `{ create_env, run_migrations, seed_data, start_services }`.
- **Concurrency Test Log Entry**: `{ request_id, status_code, response_body, elapsed_ms }`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can execute the one-shot initialization script and have all 3 services running in under 2 minutes.
- **SC-002**: 100% of setup, build, and test commands documented in `README.md` complete successfully without manual intervention.
- **SC-003**: 100% of concurrent hold collision tests output observable log proof demonstrating exactly 1 `200 OK` and `N-1` `409 Conflict` responses with zero double-holds.

## Assumptions

- PostgreSQL 15+ database is running locally or accessible via `DATABASE_URL`.
- Node.js 18+ and Python 3.11+ environments are installed on the host operating system.
