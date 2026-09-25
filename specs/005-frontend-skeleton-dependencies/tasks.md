# Tasks: Frontend Skeleton & Dependencies

**Input**: Design documents from `/specs/005-frontend-skeleton-dependencies/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend App**: `frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Next.js project configuration and environment templates

- [x] T001 Verify project structure and dependencies in `frontend/package.json`, `frontend/next.config.js`, and `frontend/.env.example`
- [x] T002 [P] Define dark glassmorphism CSS design system tokens and global styles in `frontend/app/globals.css`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Auth storage manager and API client infrastructure

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Implement SSR-safe JWT token & user session manager in `frontend/lib/auth.js`
- [x] T004 [P] Implement centralized HTTP API client with bearer token attachment and `ApiError` parsing in `frontend/lib/api.js` (depends on T003)

**Checkpoint**: Foundation ready - App Router pages and UI component scaffolds can now begin

---

## Phase 3: User Story 1 - Next.js App Router Shell & Responsive Navigation (Priority: P1) 🎯 MVP

**Goal**: Deliver a responsive App Router page hierarchy (`/`, `/login`, `/register`, `/events`, `/events/[id]`, `/orders`) with root layout embedding global header navigation and glassmorphism container styling.

**Independent Test**: Execute `npm run dev` in `frontend/` and navigate between `/`, `/login`, `/register`, `/events`, `/orders` in browser.

### Implementation for User Story 1

- [x] T005 [P] [US1] Create Root Layout with font stack and metadata in `frontend/app/layout.js`
- [x] T006 [P] [US1] Create Home Landing Page scaffold in `frontend/app/page.js`
- [x] T007 [P] [US1] Create Login Page route scaffold in `frontend/app/login/page.js`
- [x] T008 [P] [US1] Create Register Page route scaffold in `frontend/app/register/page.js`
- [x] T009 [P] [US1] Create Events Catalog route scaffold in `frontend/app/events/page.js`
- [x] T010 [P] [US1] Create Event Detail seat map route scaffold in `frontend/app/events/[id]/page.js`
- [x] T011 [P] [US1] Create Orders History route scaffold in `frontend/app/orders/page.js`

**Checkpoint**: User Story 1 (App Router Shell) is fully navigable across all 5 page routes.

---

## Phase 4: User Story 2 - Centralized API Client & JWT Token Infrastructure (Priority: P1) 🎯 MVP

**Goal**: Verify API client request dispatching, base URL concatenation from `NEXT_PUBLIC_API_URL`, JWT token header attachment, and `ApiError` status extraction (`401`, `409`, `422`).

**Independent Test**: Test `api.get()` and `api.post()` methods with valid and invalid tokens.

### Implementation for User Story 2

- [x] T012 [P] [US2] Verify environment settings fallback (`NEXT_PUBLIC_API_URL`) in `frontend/lib/api.js`
- [x] T013 [US2] Verify `Authorization: Bearer <token>` automatic header attachment in `frontend/lib/api.js`
- [x] T014 [US2] Verify custom `ApiError` class parsing status code and backend detail payload in `frontend/lib/api.js`

**Checkpoint**: User Story 2 (API Client & Auth Infrastructure) is fully functional and tested.

---

## Phase 5: User Story 3 - Shared UI Component Library Scaffold (Priority: P2)

**Goal**: Deliver modular JavaScript UI component scaffolds (`SeatGridCell`, `CountdownTimer`, `Toast`, `Navbar`) featuring status styling (`AVAILABLE`, `LOCKED`, `SOLD`, `SELECTED`), timer countdown formatting (`mm:ss`), and animated notification banners.

**Independent Test**: Render components in isolation and verify prop-driven visual states and callbacks.

### Implementation for User Story 3

- [x] T015 [P] [US3] Implement Header Navbar component (`brand`, `nav links`, `user state`) in `frontend/components/Navbar.js`
- [x] T016 [P] [US3] Implement SeatGridCell component (`AVAILABLE`, `LOCKED`, `SOLD`, `SELECTED` status styling & click handler) in `frontend/components/SeatGridCell.js`
- [x] T017 [P] [US3] Implement CountdownTimer component (`mm:ss` formatting, `<60s` warning state, `onExpire` callback) in `frontend/components/CountdownTimer.js`
- [x] T018 [P] [US3] Implement Toast notification overlay component (`success`/`error` alerts, auto-dismiss) in `frontend/components/Toast.js`

**Checkpoint**: All component scaffolds (US3) are fully functional and ready for User Flow integration in Spec 6.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Build verification and quickstart scenario validation

- [x] T019 [P] Execute `npm run build` in `frontend/` to verify zero build or SSR hydration errors
- [x] T020 Run and validate all scenarios specified in `specs/005-frontend-skeleton-dependencies/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 (App Router Shell) and US2 (API Client) are P1 MVPs and can run in parallel
  - US3 (Component Scaffolds) can run in parallel with US1/US2
- **Polish (Phase 6)**: Depends on completion of US1, US2, and US3

### Parallel Opportunities

- Tasks T005–T011 in US1 can run in parallel across separate page files
- Tasks T015–T018 in US3 can run in parallel across separate component files
- Task T019 in Polish can run in parallel with documentation checks
