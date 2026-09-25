# Tasks: Init Script & README Finalization

**Input**: Design documents from `/specs/007-init-script-readme-finalization/`

**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `contracts/init_contracts.md`, `quickstart.md`

**Tests**: Tests for core Backend API, LLM Engine, Frontend, and 15-request collision runner already exist. Documentation and initialization runner verification tasks are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project configuration check and environment template baseline verification

- [x] T001 Verify and align `.env.example` templates across root `.env.example`, `backend/.env.example`, `llm-engine/.env.example`, and `frontend/.env.example`
- [x] T002 [P] Verify directory paths and entry points for `scripts/run_migrations.py` and `scripts/seed_event.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared utilities for cross-platform runner and pre-flight health checks

**⚠️ CRITICAL**: Must be completed before user story initialization scripts execute

- [x] T003 Implement PostgreSQL database connection pre-flight check utility in `init.py`
- [x] T004 [P] Implement CLI argument parsing (`--skip-env`, `--skip-migrations`, `--skip-seed`, `--skip-services`) in `init.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - One-Shot Automated Environment & Services Initialization (Priority: P1) 🎯 MVP

**Goal**: Execute a single one-shot initialization command (`python init.py` or `.\init.ps1`) that auto-creates `.env` files from templates, runs Alembic migrations (`scripts/run_migrations.py`), executes DML event seeding (`scripts/seed_event.py`), and spawns Backend (:8000), LLM Engine (:8001), and Frontend (:3000) services concurrently.

**Independent Test**: Run `python init.py` or `.\init.ps1` on a clean workspace, verify that `.env` files exist, database migrations/seeding complete cleanly, and all 3 services respond on ports 8000, 8001, and 3000.

### Implementation for User Story 1

- [x] T005 [P] [US1] Implement environment template copy logic (`.env.example` -> `.env`) with overwrite preservation in `init.py`
- [x] T006 [US1] Implement migration runner (`scripts/run_migrations.py`) and seeding runner (`scripts/seed_event.py`) execution step in `init.py`
- [x] T007 [US1] Implement multi-service async subprocess spawner and port conflict detector (8000, 8001, 3000) in `init.py`
- [x] T008 [P] [US1] Create PowerShell entry wrapper script in `init.ps1`

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Comprehensive Project Architecture & Setup Documentation (Priority: P1) 🎯 MVP

**Goal**: Create a comprehensive root `README.md` detailing multi-tier architecture, system design, environment variable reference, setup walkthrough, and test suite commands.

**Independent Test**: Read `README.md` and follow setup, build (`npm run build`), and test (`pytest`) instructions step-by-step on a clean environment.

### Implementation for User Story 2

- [x] T009 [P] [US2] Write executive architectural summary, technology stack choices, and 4-tier system structure in `README.md`
- [x] T010 [P] [US2] Write detailed `.env.example` walkthrough explaining all configuration variables for root, backend, llm-engine, and frontend in `README.md`
- [x] T011 [US2] Write complete setup, one-shot initialization (`init.py` / `init.ps1`), and test suite execution guide (`pytest`, `npm run build`) in `README.md`

**Checkpoint**: At this point, User Stories 1 AND 2 are fully functional and documented.

---

## Phase 5: User Story 3 - Concurrency Correctness Proof & Test Reproduction Guide (Priority: P2)

**Goal**: Document the 6-step Concurrency Correctness Design Note in `README.md` and provide step-by-step instructions to execute and interpret the 15-request concurrent collision test (`backend/tests/test_concurrency.py`).

**Independent Test**: Execute `python backend/tests/test_concurrency.py` as documented in `README.md` and observe log-based proof demonstrating exactly 1 `200 OK` winner alongside 14 `409 Conflict` rejections with zero database double-holds.

### Implementation for User Story 3

- [x] T012 [P] [US3] Write 6-step Concurrency Correctness Design Note (PostgreSQL row locking, `NOWAIT` lock manager rejection, single-transaction atomic predicates, short lock duration, redundant lease expiration, atomic checkout safeguards) in `README.md`
- [x] T013 [US3] Write step-by-step reproduction instructions and log-based proof output guide for `backend/tests/test_concurrency.py` in `README.md`

**Checkpoint**: All user stories are independently functional and fully documented.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cross-platform verification and final execution validation

- [x] T014 [P] Perform cross-platform syntax and execution check for `init.py` and `init.ps1` across Windows and POSIX shells
- [x] T015 Execute full validation suite per `specs/007-init-script-readme-finalization/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 (P1) and US2 (P1) can proceed in parallel or sequentially
  - US3 (P2) depends on US2 README documentation foundation
- **Polish (Phase 6)**: Depends on completion of User Stories 1, 2, and 3

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Documents US1 setup commands
- **User Story 3 (P2)**: Can start after US2 - Extends `README.md` with Concurrency Design Note & test reproduction steps

### Parallel Opportunities

- T002 (Setup paths) can run in parallel with T001
- T004 (CLI arg parsing) can run in parallel with T003
- T005 (Env copy logic) and T008 (PowerShell wrapper) can run in parallel within US1
- T009 (Architecture overview) and T010 (.env walkthrough) can run in parallel within US2
- T012 (Concurrency Design Note) can run in parallel with T011/T013
- T014 (Cross-platform checks) can run in parallel with T015 validation

---

## Parallel Example: User Story 1

```powershell
# Implement environment file copy logic and PowerShell wrapper concurrently:
Task: "T005 [P] [US1] Implement environment template copy logic (.env.example -> .env) with overwrite preservation in init.py"
Task: "T008 [P] [US1] Create PowerShell entry wrapper script in init.ps1"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

1. Complete Phase 1: Setup & Phase 2: Foundational
2. Complete Phase 3: User Story 1 (`init.py` & `init.ps1`)
3. Complete Phase 4: User Story 2 (`README.md` core documentation)
4. **VALIDATE**: Run `python init.py` to verify system initialization and check README clarity.

### Incremental Delivery

1. Foundation + One-Shot Init Script (US1) → System runs in 1 command (MVP!)
2. Add Full Architecture & Setup Documentation (US2) → Developer onboarding ready
3. Add Concurrency Correctness Design Note & Test Instructions (US3) → Technical audit proof complete

---

## Notes

- All tasks follow strict format: `- [ ] TXXX [P?] [US?] Description with file path`
- File paths are explicitly specified for every task
- Zero secret leakage policy enforced across all `.env.example` templates and script logging
