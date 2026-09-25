# Tasks: Core Backend API (Ticketing)

**Input**: Design documents from `specs/002-backend-api-ticketing/`

**Prerequisites**: `plan.md` (required), `spec.md` (required), `data-model.md`, `contracts/api-contract.md`, `quickstart.md`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Backend configuration, Pydantic settings, and core application package initialization.

- [x] T001 Create backend environment configuration management in `backend/app/config.py` loading `DATABASE_URL`, `JWT_SECRET`, `HOLD_DURATION_SECONDS`, and connection pool settings
- [x] T002 [P] Create main FastAPI application entrypoint in `backend/app/main.py` with CORS middleware and global exception handlers

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database engine connection pooling, SQLAlchemy ORM models, and API router setup.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 Configure primary request connection pool ($\ge 15$ connections) and isolated sweeper pool in `backend/app/db/session.py`
- [x] T004 [P] Define SQLAlchemy ORM domain models (`User`, `Event`, `Seat`, `Hold`, `Order`, `Ticket`) in `backend/app/models/domain.py`
- [x] T005 [P] Define Pydantic request and response DTO schemas in `backend/app/schemas/dto.py`
- [x] T006 Initialize central FastAPI router aggregation in `backend/app/api/router.py`

**Checkpoint**: Foundational database connection pools, domain models, and schemas ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - User Authentication & Identity Protection (Priority: P1) 🎯 MVP

**Goal**: Complete user registration (`POST /auth/register`), login (`POST /auth/login`), JWT issuance, and claims-based auth dependency (`get_current_user`).

**Independent Test**: Execute `pytest backend/tests/test_auth.py` verifying registration, password hashing, login token issuance, and JWT claim decoding.

- [x] T007 [P] [US1] Implement password hashing (`bcrypt`) and JWT token encoding/decoding utilities in `backend/app/core/security.py`
- [x] T008 [P] [US1] Implement authenticated user dependency `get_current_user` in `backend/app/core/dependencies.py` deriving user identity strictly from JWT claims
- [x] T009 [US1] Implement registration and login API endpoints in `backend/app/api/v1/auth.py`
- [x] T010 [US1] Implement automated unit and API integration tests for authentication in `backend/tests/test_auth.py`

**Checkpoint**: User Story 1 (Auth & Identity Protection) fully functional and testable independently.

---

## Phase 4: User Story 2 - Event Discovery & Real-Time Seat Map Browsing (Priority: P1) 🎯 MVP

**Goal**: Implement event listing (`GET /events`) and seat map browsing (`GET /events/{id}/seats`) with dynamic lazy-expiry calculation on read.

**Independent Test**: Execute `pytest backend/tests/test_events.py` verifying event catalog listing and lazy expiration projecting expired locked seats as `AVAILABLE`.

- [x] T011 [P] [US2] Implement event listing endpoint (`GET /events`) in `backend/app/api/v1/events.py`
- [x] T012 [US2] Implement seat map endpoint (`GET /events/{id}/seats`) in `backend/app/api/v1/events.py` with dynamic lazy-expiry calculation projecting expired holds as `AVAILABLE`
- [x] T013 [US2] Implement unit and API tests for event listing and seat map lazy expiration in `backend/tests/test_events.py`

**Checkpoint**: User Story 2 (Event Discovery & Seat Map) functional and testable independently.

---

## Phase 5: User Story 3 - Atomic Concurrency-Safe Seat Hold Acquisition (Priority: P1) 🎯 MVP

**Goal**: Implement non-blocking, deadlock-immune seat hold acquisition (`POST /events/{id}/holds`) using raw parameterized SQL (`text()`), `LEFT JOIN`, `ORDER BY id ASC`, `FOR UPDATE OF s NOWAIT`, and atomic count validation.

**Independent Test**: Execute `pytest backend/tests/test_holds.py` verifying single and multi-seat hold acquisition, non-blocking lock contention, and all-or-nothing rollback on partial seat unavailability.

- [x] T014 [US3] Implement hold acquisition endpoint (`POST /events/{id}/holds`) in `backend/app/api/v1/holds.py` executing raw parameterized SQL (`text()`) with `ORDER BY id ASC`, `LEFT JOIN`, `SELECT ... FOR UPDATE OF s NOWAIT`, and HTTP 409 Conflict exception handling on error 55P03 or row count mismatch
- [x] T015 [US3] Implement unit and integration tests for hold acquisition and lock contention in `backend/tests/test_holds.py`

**Checkpoint**: User Story 3 (Atomic Seat Hold Acquisition) functional and testable independently.

---

## Phase 6: User Story 4 - Atomic Checkout & Order Completion (Priority: P1) 🎯 MVP

**Goal**: Implement atomic checkout (`POST /holds/{hold_id}/checkout`) with mock payment execution, conditional seat update (`status = 'SOLD'`), `COMPLETED`/`order_id` write, mock refund on failure, and order history (`GET /orders`).

**Independent Test**: Execute `pytest backend/tests/test_checkout.py` verifying hold checkout, ticket creation, mock refund on zero-row update, and JWT-derived order history.

- [x] T016 [P] [US4] Implement mock payment stub and refund callback functions in `backend/app/core/payment.py`
- [x] T017 [US4] Implement atomic checkout endpoint (`POST /holds/{hold_id}/checkout`) in `backend/app/api/v1/checkout.py` executing conditional raw SQL update (`status = 'SOLD'`), order/ticket creation, and mock refund triggering on zero-row update failure
- [x] T018 [P] [US4] Implement customer order history endpoint (`GET /orders`) in `backend/app/api/v1/orders.py` filtering strictly by JWT user ID claim
- [x] T019 [US4] Implement integration tests for checkout, refund handling, and order history in `backend/tests/test_checkout.py`

**Checkpoint**: User Story 4 (Atomic Checkout & Orders) functional and testable independently.

---

## Phase 7: User Story 5 - Explicit Hold Release (Priority: P2)

**Goal**: Implement explicit hold release (`DELETE /holds/{hold_id}`) with JWT ownership verification returning seats to `AVAILABLE` status.

**Independent Test**: Test explicit release via `DELETE /holds/{hold_id}` verifying seats return to `AVAILABLE` immediately and non-owners receive HTTP 403.

- [x] T020 [US5] Implement explicit hold release endpoint (`DELETE /holds/{hold_id}`) in `backend/app/api/v1/holds.py` verifying caller JWT ownership, updating hold status to `EXPIRED`, and resetting seats to `AVAILABLE`
- [x] T021 [US5] Add integration tests for explicit hold release and ownership authorization in `backend/tests/test_holds.py`

**Checkpoint**: User Story 5 (Explicit Hold Release) functional and testable independently.

---

## Phase 8: User Story 6 - Asynchronous Lease Sweeper & Natural Language AI Search Stub (Priority: P3)

**Goal**: Implement background lease sweeper worker (`SKIP LOCKED` 15-30s interval) and AI search endpoint stub (`POST /events/{id}/ai-search`).

**Independent Test**: Execute tests verifying sweeper recycles expired holds without blocking active checkouts, and AI search stub returns Pydantic-validated seat preferences.

- [x] T022 [P] [US6] Implement background lease sweeper worker task in `backend/app/workers/sweeper.py` executing `SELECT ... FOR UPDATE SKIP LOCKED` on expired holds using isolated database connection pool
- [x] T023 [P] [US6] Implement natural language AI search endpoint stub (`POST /events/{id}/ai-search`) in `backend/app/api/v1/events.py` returning Pydantic-validated candidate seat preferences
- [x] T024 [US6] Integrate sweeper worker lifecycle into FastAPI startup/shutdown events in `backend/app/main.py`
- [x] T025 [US6] Add unit tests for background sweeper worker and AI search stub endpoint in `backend/tests/test_sweeper.py`

**Checkpoint**: All user stories implemented and functional independently.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Mandatory concurrency collision suite, OpenAPI contract verification, and quickstart validation.

- [x] T026 Implement automated high-concurrency collision test suite (10+ simultaneous requests targeting identical seats using `httpx` & `asyncio.gather`) in `backend/tests/test_concurrency.py` verifying exactly 1 HTTP 200 OK and $N-1$ HTTP 409 Conflicts
- [x] T027 [P] Execute quickstart validation guide in `specs/002-backend-api-ticketing/quickstart.md` verifying end-to-end API workflows

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories.
- **User Stories (Phases 3–8)**: All depend on Foundational phase completion.
  - Can proceed sequentially in priority order (US1 → US2 → US3 → US4 → US5 → US6).
- **Polish (Phase 9)**: Depends on User Stories 1–6 being complete.

### Parallel Opportunities

- **Phase 2**: T004 (models), T005 (DTOs), and T006 (router initialization) can run in parallel.
- **Phase 3**: T007 (security) and T008 (auth dependency) can run in parallel before T009 (auth router).
- **Phase 6**: T016 (payment stub) and T018 (orders history) can run in parallel.
- **Phase 8**: T022 (sweeper worker) and T023 (AI search stub) can run in parallel.

---

## Implementation Strategy

### MVP First (User Stories 1–4)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: Foundational (T003, T004, T005, T006)
3. Complete Phase 3: User Story 1 (Auth & Identity)
4. Complete Phase 4: User Story 2 (Event Catalog & Seat Map)
5. Complete Phase 5: User Story 3 (Atomic Seat Hold Acquisition)
6. Complete Phase 6: User Story 4 (Atomic Checkout & Orders)
7. **VALIDATE**: Run `pytest backend/tests/test_concurrency.py` to verify double-selling immunity.

### Incremental Delivery

1. Setup + Foundational → Backend framework & connection pools ready.
2. User Story 1 → JWT Auth API live.
3. User Story 2 → Event & Seat Map API live (4s polling).
4. User Story 3 → Hold Acquisition live (Concurrency-safe MVP!).
5. User Story 4 → Checkout & Orders live (Full purchasing lifecycle MVP!).
6. User Story 5 → Explicit Release live.
7. User Story 6 → Sweeper Worker & AI Search stub live.
8. Polish → High-concurrency collision test suite verified.
