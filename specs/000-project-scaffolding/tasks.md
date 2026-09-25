# Tasks: Project Scaffolding & Tooling

**Input**: Design documents from `specs/000-project-scaffolding/`

**Prerequisites**: `plan.md` (required), `spec.md` (required), `data-model.md`, `contracts/env-contract.md`, `quickstart.md`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Repository initialization, top-level layout, and git secret safety configuration.

- [x] T001 Create top-level project directory structure (`frontend/`, `backend/`, `llm-engine/`, `scripts/`) matching Constitution Section 8
- [x] T002 [P] Configure root `.gitignore` to strictly exclude `.env`, `.env.local`, `.venv/`, `__pycache__/`, `node_modules/`, and build artifacts per Constitution Principle VII

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Base package initialization across all microservices before user story execution.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 [P] Initialize `backend/` Python project structure with `pyproject.toml` managed by `uv`
- [x] T004 [P] Initialize `llm-engine/` Python project structure with `pyproject.toml` managed by `uv`
- [x] T005 [P] Initialize `frontend/` Next.js App Router project using JavaScript (`.js` / `.jsx`) in `frontend/package.json`

**Checkpoint**: Base project packages ready — user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Independent Microservice Environment Setup (Priority: P1) 🎯 MVP

**Goal**: Completely decoupled directory structures and independent dependency management for `backend/`, `llm-engine/`, and `frontend/` without virtualenv leaks.

**Independent Test**: Run `uv sync` in `backend/` and `llm-engine/` verifying separate `uv.lock` files, and `npm install` in `frontend/`.

- [x] T006 [P] [US1] Configure dependencies in `backend/pyproject.toml` (`fastapi`, `sqlalchemy`, `asyncpg`, `pydantic`, `alembic`, `pytest`, `pytest-asyncio`, `httpx`) and generate `backend/uv.lock`
- [x] T007 [P] [US1] Configure dependencies in `llm-engine/pyproject.toml` (`fastapi`, `pydantic`, `google-genai`) and generate `llm-engine/uv.lock`
- [x] T008 [P] [US1] Create Next.js App Router configuration and base layout in `frontend/next.config.js` and `frontend/app/layout.js`
- [x] T009 [US1] Verify independent virtual environment activation and dependency isolation across `backend/` and `llm-engine/`

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Zero-Secret Configuration & Example Environments (Priority: P2)

**Goal**: Standardized `.env.example` files across all microservices containing documented configuration keys without committing secrets.

**Independent Test**: Verify presence of `.env.example` in all service directories and assert `git status` ignores copied `.env` files.

- [x] T010 [P] [US2] Create `backend/.env.example` with `DATABASE_URL`, `JWT_SECRET`, `JWT_ALGORITHM`, `HOLD_DURATION_SECONDS`, and `LLM_ENGINE_URL` placeholders per contract `specs/000-project-scaffolding/contracts/env-contract.md`
- [x] T011 [P] [US2] Create `llm-engine/.env.example` with `GEMINI_API_KEY`, `LLM_PROVIDER`, and `PORT` placeholders per contract `specs/000-project-scaffolding/contracts/env-contract.md`
- [x] T012 [P] [US2] Create `frontend/.env.example` with `NEXT_PUBLIC_API_BASE_URL` placeholder per contract `specs/000-project-scaffolding/contracts/env-contract.md`
- [x] T013 [US2] Validate that active `.env` files in `backend/`, `llm-engine/`, and `frontend/` are ignored by `.gitignore` and git tracking checks

**Checkpoint**: User Stories 1 AND 2 work independently and satisfy security hygiene rules.

---

## Phase 5: User Story 3 - Database Migration Infrastructure (Priority: P3)

**Goal**: Alembic migration setup under `backend/alembic/` and a cross-platform Python migration runner script in `scripts/run_migrations.py`.

**Independent Test**: Execute `python scripts/run_migrations.py` with valid database configuration.

- [x] T014 [US3] Initialize Alembic configuration in `backend/alembic.ini` and `backend/alembic/env.py` configured for SQLAlchemy `asyncpg` engine connection
- [x] T015 [US3] Implement cross-platform Python migration runner script in `scripts/run_migrations.py` supporting CLI args and loading `DATABASE_URL` from `backend/.env` per contract `specs/000-project-scaffolding/contracts/env-contract.md`
- [x] T016 [US3] Verify migration runner error handling when database configuration is unconfigured or invalid

**Checkpoint**: All 3 user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and end-to-end quickstart validation.

- [x] T017 [P] Create repository `README.md` summarizing multi-service architecture, setup instructions, and quickstart validation guide
- [x] T018 Run quickstart validation guide in `specs/000-project-scaffolding/quickstart.md` to verify end-to-end repository initialization

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories.
- **User Stories (Phases 3–5)**: All depend on Foundational phase completion.
  - Can proceed sequentially in priority order (US1 → US2 → US3) or in parallel where files do not overlap.
- **Polish (Phase 6)**: Depends on User Stories 1–3 being complete.

### Parallel Opportunities

- **Phase 1**: T001 and T002 can run in parallel.
- **Phase 2**: T003 (`backend/`), T004 (`llm-engine/`), and T005 (`frontend/`) can run in parallel.
- **Phase 3 (US1)**: T006, T007, and T008 can run in parallel.
- **Phase 4 (US2)**: T010, T011, and T012 can run in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: Foundational (T003, T004, T005)
3. Complete Phase 3: User Story 1 (T006, T007, T008, T009)
4. **VALIDATE**: Verify independent virtual environments and `uv.lock` generation.

### Incremental Delivery

1. Setup + Foundational → Repository structure ready.
2. User Story 1 → Isolated `uv` Python environments and Next.js setup (MVP!).
3. User Story 2 → Zero-secret `.env.example` templates and `.gitignore` safety.
4. User Story 3 → Alembic setup and `scripts/run_migrations.py` runner script.
5. Polish → `README.md` and `quickstart.md` validation pass.
