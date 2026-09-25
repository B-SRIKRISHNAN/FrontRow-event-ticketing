# Feature Specification: Frontend User Flows

**Feature Branch**: `006-frontend-user-flows`

**Created**: 2026-09-25

**Status**: Draft

**Input**: User description: "Spec 6 — Frontend User Flows: Each flow as an acceptance-scenario section within this one spec: Register / login; Browse events -> seat map view (available/held/sold, 4s polling); Select seats -> hold -> countdown timer -> checkout; Orders/tickets view; AI search input -> candidate seats -> manual fallback path."

## Clarifications

### Session 2026-09-25

- Q: Next.js language stack? → A: JavaScript (`.jsx` / `.js`) as established in Spec 5.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authentication Flow: User Registration & Login (Priority: P1) 🎯 MVP

As a ticket buyer, I want to register a new account or log in with my email and password so that I receive a JWT bearer token to perform authenticated seat holds, checkouts, and view my order history.

**Why this priority**: Required for identity enforcement (Constitution Principle II). Authenticated JWT bearer tokens are required to acquire holds, execute checkouts, and query user orders.

**Independent Test**: Can be tested independently by submitting `/register` and `/login` forms, observing token storage in `lib/auth.js`, checking navbar header auth state changes, and verifying authenticated API access.

**Acceptance Scenarios**:

1. **Given** a new user on `/register`, **When** they submit email and password ($\ge 8$ chars), **Then** the app calls `POST /api/v1/auth/register`, creates the account, acquires JWT token, stores it in auth storage, updates Navbar, and redirects to `/events`.
2. **Given** an existing user on `/login`, **When** they submit valid credentials, **Then** the app calls `POST /api/v1/auth/login`, stores JWT token, updates Navbar with user email, and redirects to `/events`.
3. **Given** invalid credentials or password $< 8$ chars, **When** submitted, **Then** the app displays a clear Toast error message without redirecting or altering auth state.

---

### User Story 2 - Event Browsing & Real-Time Seat Map Polling Flow (Priority: P1) 🎯 MVP

As a ticket buyer, I want to browse the event catalog and view an interactive seat map with real-time seat status updates (polling every 4 seconds) so that I always see live seat availability (`AVAILABLE`, `LOCKED`, `SOLD`) without manually refreshing the browser.

**Why this priority**: Core event discovery and seat map visibility required prior to seat selection and hold acquisition.

**Independent Test**: Can be tested independently by opening `/events`, clicking an event to view `/events/[id]`, observing seat statuses (`AVAILABLE`, `LOCKED`, `SOLD`), and verifying network polling requests every 4 seconds.

**Acceptance Scenarios**:

1. **Given** a user on `/events`, **When** the page loads, **Then** the app calls `GET /api/v1/events` and renders event cards with venue name, show time, and "View Seat Map" button.
2. **Given** a user on `/events/[id]`, **When** the seat map loads, **Then** the app calls `GET /api/v1/events/{id}/seats` and renders seats using `SeatGridCell` with green for `AVAILABLE`, amber for `LOCKED`, and muted gray for `SOLD`.
3. **Given** a user viewing `/events/[id]`, **When** 4 seconds elapse, **Then** the app background-polls `GET /api/v1/events/{id}/seats` and silently updates seat statuses on the map without flickering or resetting user selections.

---

### User Story 3 - Interactive Seat Selection, Hold Lease & Checkout Flow (Priority: P1) 🎯 MVP

As an authenticated ticket buyer, I want to select available seats, acquire a 5-minute hold lease with an active countdown timer, and complete mock payment checkout before expiry so that my seats transition to `SOLD` and generate confirmed tickets.

**Why this priority**: Fundamental core flow of the ticketing platform (Constitution Principle I & III). Exercises atomic hold acquisition, lease countdown, checkout payment stub, and lock contention handling.

**Independent Test**: Can be tested independently by selecting available seats, clicking "Hold Seats", observing the 5-minute `CountdownTimer`, clicking "Complete Checkout", and asserting seats transition to `SOLD` state.

**Acceptance Scenarios**:

1. **Given** selected available seats on `/events/[id]`, **When** the user clicks "Hold Seats", **Then** the app calls `POST /api/v1/events/{id}/holds`, displays an active 5-minute `CountdownTimer`, updates held seats to `SELECTED`, and shows a "Proceed to Checkout" panel.
2. **Given** an active hold lease, **When** the user clicks "Complete Checkout" with mock payment, **Then** the app calls `POST /api/v1/checkout/holds/{holdId}`, converts seats to `SOLD`, shows a Toast success banner ("Checkout Successful!"), and redirects to `/orders`.
3. **Given** a hold lease that expires before checkout or a lock collision (`409 Conflict`), **When** triggered, **Then** the app displays a Toast error ("Hold expired or lock conflict detected"), clears active hold timer, and refreshes the seat map.

---

### User Story 4 - Order History & Ticket Receipt Flow (Priority: P2)

As an authenticated user, I want to visit `/orders` to view my past orders, order dates, total amounts, and ticket seat assignments so that I have a record of my confirmed purchases.

**Why this priority**: Completes the post-purchase user experience by rendering confirmed tickets and order details.

**Independent Test**: Can be tested independently by navigating to `/orders` and verifying rendered order cards match purchases created during checkout.

**Acceptance Scenarios**:

1. **Given** an authenticated user on `/orders`, **When** the page loads, **Then** the app calls `GET /api/v1/orders` and renders order history cards displaying Order ID, purchase date, total amount, and individual ticket details (Row, Seat Number, Price Paid).
2. **Given** a user with zero orders, **When** `/orders` loads, **Then** the page displays a clean empty state card ("No Orders Purchased Yet") with a button to browse events.

---

### User Story 5 - AI Natural Language Seat Search & Manual Fallback Flow (Priority: P2)

As a ticket buyer, I want to type natural language queries (e.g. "Find me 2 seats together under $150") into an AI search box on the seat map page so that recommended candidate seats are automatically highlighted or manual selection advice is provided if fallback occurs.

**Why this priority**: Integrates Spec 4's LLM Engine microservice into the frontend user interface, fulfilling natural language candidate seat selection.

**Independent Test**: Can be tested independently by typing search prompts into the AI search bar on `/events/[id]` and verifying candidate seat highlights or manual fallback toasts.

**Acceptance Scenarios**:

1. **Given** a user on `/events/[id]`, **When** they type "2 seats together" into the AI search input and click "Search", **Then** the app calls `POST /api/v1/events/{id}/ai-search` and automatically highlights returned candidate seat IDs as `SELECTED`.
2. **Given** an AI search response returning `fallback_to_manual: true` or zero candidate seats, **When** received, **Then** the app displays an informative Toast ("AI recommendation unavailable or no exact match found. Please select seats manually on the grid.") and allows standard manual seat picking.

---

### Edge Cases

- What happens if the user attempts to click "Hold Seats" without being logged in? The app displays a Toast error ("Please log in to hold seats") and redirects to `/login`.
- What happens if 4-second polling encounters a network interruption? The polling mechanism suppresses transient network errors silently, retrying on the next 4-second tick without interrupting user seat selections.
- What happens if the user navigates away from `/events/[id]` with an active hold? The hold remains active on the backend until its 5-minute lease expires or sweeper recycles it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement complete frontend user flows in JavaScript (`.jsx` / `.js`) across Next.js App Router routes (`/`, `/login`, `/register`, `/events`, `/events/[id]`, `/orders`).
- **FR-002**: `/register` and `/login` pages MUST process form submissions, call backend authentication endpoints (`POST /api/v1/auth/register`, `POST /api/v1/auth/login`), store JWT token in `lib/auth.js`, update Navbar header state, and redirect to `/events`.
- **FR-003**: `/events` page MUST fetch and display upcoming event cards from `GET /api/v1/events`.
- **FR-004**: `/events/[id]` seat map page MUST fetch seat map from `GET /api/v1/events/{id}/seats` and establish a 4-second polling interval (`setInterval`) to update live seat status badges (`AVAILABLE`, `LOCKED`, `SOLD`) dynamically.
- **FR-005**: `/events/[id]` page MUST allow users to select available seats, click "Hold Seats" (`POST /api/v1/events/{id}/holds`), display `CountdownTimer` for the 5-minute lease, and present a "Complete Checkout" button.
- **FR-006**: Checkout process MUST submit `POST /api/v1/checkout/holds/{holdId}` with mock payment token, convert seats to `SOLD`, display Toast success notice, and redirect to `/orders`.
- **FR-007**: `/orders` page MUST fetch and display confirmed user orders and tickets from `GET /api/v1/orders`.
- **FR-008**: `/events/[id]` page MUST render an AI search input box calling `POST /api/v1/events/{id}/ai-search`, highlighting candidate seats, or displaying a manual fallback Toast if `fallback_to_manual: true`.

### Key Entities *(include if feature involves data)*

- **Auth Session Payload**: `{ token, email }`.
- **Hold Session State**: `{ holdId, expiresAt, seatIds, status }`.
- **AI Search Query Payload**: `{ query }`.
- **Checkout Payment Payload**: `{ payment_token }`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete registration, event browsing, seat selection, hold acquisition, and checkout in under 2 minutes.
- **SC-002**: 100% of seat map views on `/events/[id]` poll live seat availability every 4 seconds without UI flicker or lost selections.
- **SC-003**: 100% of expired holds or lock contention errors (`409 Conflict`) display user-friendly Toast alerts and gracefully reset hold timer UI.

## Assumptions

- Backend API (`http://localhost:8000`) and LLM Engine (`http://localhost:8001`) are running during end-to-end user flow execution.
- Next.js 14 App Router and Vanilla CSS design system tokens from Spec 5 are utilized across all page routes.
