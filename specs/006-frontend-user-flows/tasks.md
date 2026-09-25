# Tasks: Frontend User Flows

**Input**: Design documents from `/specs/006-frontend-user-flows/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend App**: `frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify Next.js frontend setup and environment configuration

- [x] T001 Verify API base URL configuration in `frontend/.env.local` / `frontend/.env.example`
- [x] T002 [P] Verify API client helper in `frontend/lib/api.js` and auth helper in `frontend/lib/auth.js`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Custom event bus for auth state synchronization across components

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add `auth-change` event listener and state sync in `frontend/components/Navbar.js`

**Checkpoint**: Foundation ready - User flows implementation can now begin

---

## Phase 3: User Story 1 - Authentication Flow: User Registration & Login (Priority: P1) 🎯 MVP

**Goal**: Deliver complete user registration (`/register`) and login (`/login`) form submission flows with JWT bearer token storage, Navbar state synchronization, and redirect to `/events`.

**Independent Test**: Register a new user on `/register` or login on `/login`, verify JWT token saved to auth storage, Navbar displays email, and page redirects to `/events`.

### Implementation for User Story 1

- [x] T004 [P] [US1] Implement registration form handler and API submission (`POST /api/v1/auth/register`) in `frontend/app/register/page.js`
- [x] T005 [P] [US1] Implement login form handler and API submission (`POST /api/v1/auth/login`) in `frontend/app/login/page.js`
- [x] T006 [US1] Add Toast error banner handling for invalid credentials and duplicate registration in `frontend/app/login/page.js` and `frontend/app/register/page.js` (depends on T004, T005)

**Checkpoint**: User Story 1 (Auth Flow) is fully functional and testable independently.

---

## Phase 4: User Story 2 - Event Browsing & Real-Time Seat Map Polling Flow (Priority: P1) 🎯 MVP

**Goal**: Deliver event catalog browsing (`GET /api/v1/events`) and interactive seat map loading (`GET /api/v1/events/{id}/seats`) with a 4-second background polling loop (`setInterval`) updating live seat statuses (`AVAILABLE`, `LOCKED`, `SOLD`) without UI flicker.

**Independent Test**: Navigate to `/events`, select an event to open `/events/[id]`, observe seat map rendering, and verify 4-second network polling requests in browser network tab.

### Implementation for User Story 2

- [x] T007 [P] [US2] Implement live event catalog fetching and card rendering in `frontend/app/events/page.js`
- [x] T008 [P] [US2] Implement initial seat map fetching and seat grid rendering in `frontend/app/events/[id]/page.js`
- [x] T009 [US2] Implement 4-second background polling interval (`setInterval`) with silent seat map state updates in `frontend/app/events/[id]/page.js` (depends on T008)

**Checkpoint**: User Story 2 (Event Catalog & 4s Polling) is fully functional and updating live seat states.

---

## Phase 5: User Story 3 - Interactive Seat Selection, Hold Lease & Checkout Flow (Priority: P1) 🎯 MVP

**Goal**: Deliver interactive seat selection, hold lease acquisition (`POST /events/{id}/holds`), 5-minute `CountdownTimer` display, mock payment checkout (`POST /checkout/holds/{holdId}`), seat conversion to `SOLD`, and Toast error handling for unauthenticated attempts, expired holds, or lock contention (`409 Conflict`).

**Independent Test**: Select available seats, click "Hold Seats", verify active `CountdownTimer`, click "Complete Checkout", and confirm seats transition to `SOLD` state and redirect to `/orders`.

### Implementation for User Story 3

- [x] T010 [P] [US3] Implement interactive seat selection state management in `frontend/app/events/[id]/page.js`
- [x] T011 [US3] Implement hold acquisition handler (`POST /api/v1/events/{id}/holds`), active hold state, and `CountdownTimer` integration in `frontend/app/events/[id]/page.js` (depends on T010)
- [x] T012 [US3] Implement mock payment checkout handler (`POST /api/v1/checkout/holds/{holdId}`) and success redirect to `/orders` in `frontend/app/events/[id]/page.js` (depends on T011)
- [x] T013 [US3] Implement Toast error alerts for unauthenticated hold attempts, hold lease expirations, and `409 Conflict` lock contention in `frontend/app/events/[id]/page.js` (depends on T011, T012)

**Checkpoint**: User Story 3 (Seat Selection, Hold Lease & Checkout) is fully functional and guarantees Principle I & III lifecycle rules.

---

## Phase 6: User Story 4 - Order History & Ticket Receipt Flow (Priority: P2)

**Goal**: Deliver user order history page (`GET /api/v1/orders`) on `/orders` rendering confirmed purchases with Order ID, purchase timestamp, total amount, and individual ticket badges (Row, Seat Number, Price Paid).

**Independent Test**: Complete a checkout flow and navigate to `/orders` to verify purchase receipt details.

### Implementation for User Story 4

- [x] T014 [P] [US4] Implement authenticated orders fetching (`GET /api/v1/orders`) and order card list rendering in `frontend/app/orders/page.js`
- [x] T015 [P] [US4] Implement empty order history state card with "Browse Events" CTA button in `frontend/app/orders/page.js`

**Checkpoint**: User Story 4 (Order History) is fully functional and displaying confirmed ticket receipts.

---

## Phase 7: User Story 5 - AI Natural Language Seat Search & Manual Fallback Flow (Priority: P2)

**Goal**: Deliver AI natural language search box on seat map page calling `POST /api/v1/events/{id}/ai-search`, automatically highlighting returned candidate seat IDs, or presenting an informative Toast advice banner if `fallback_to_manual: true`.

**Independent Test**: Type `2 seats together under $150` into the AI search box on `/events/1` and verify candidate seat highlighting.

### Implementation for User Story 5

- [x] T016 [P] [US5] Implement AI search input form and API submission (`POST /api/v1/events/{id}/ai-search`) in `frontend/app/events/[id]/page.js`
- [x] T017 [US5] Implement candidate seat auto-highlighting (`selectedSeatIds`) and manual fallback Toast notice handling in `frontend/app/events/[id]/page.js` (depends on T016)

**Checkpoint**: All 5 user stories (US1–US5) are fully integrated and functional.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Build verification and end-to-end quickstart validation

- [x] T018 [P] Execute `npm run build` in `frontend/` to verify zero build or SSR hydration errors
- [x] T019 Run and validate all end-to-end scenarios specified in `specs/006-frontend-user-flows/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 (Auth), US2 (Event Catalog & Polling), US3 (Hold & Checkout) are P1 MVPs
  - US4 (Orders) depends on US3 checkout flow
  - US5 (AI Search) can run in parallel with US2/US3
- **Polish (Phase 8)**: Depends on completion of all user stories (US1–US5)

### Parallel Opportunities

- Tasks T004, T005 in US1 can run in parallel across login/register page files
- Tasks T007, T008 in US2 can run in parallel across event catalog & detail page files
- Tasks T014, T015 in US4 can run in parallel inside orders page
- Task T018 in Polish can run in parallel with documentation checks

---

## Phase 9: Convergence

**Purpose**: Track findings and remediations identified during convergence assessment

- [x] T020 Add route alias `@router.post("/checkout/holds/{hold_id}")` in `backend/app/api/v1/checkout.py` per `contracts/user_flow_contracts.md` and `US3/AC2` (`partial`)
- [x] T021 Update seat map legend color swatches and add CSS status tokens in `frontend/app/events/[id]/page.js` and `frontend/app/globals.css` per `US2/AC2` (`partial`)
- [x] T022 Add manual "Cancel Hold" button calling `DELETE /api/v1/holds/{hold_id}` in `frontend/app/events/[id]/page.js` per `US3/AC1` (`partial`)


