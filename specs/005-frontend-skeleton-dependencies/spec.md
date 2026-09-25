# Feature Specification: Frontend Skeleton & Dependencies

**Feature Branch**: `005-frontend-skeleton-dependencies`

**Created**: 2026-09-25

**Status**: Draft

**Input**: User description: "Spec 5 — Frontend Skeleton & Dependencies: Next.js project structure, routing, base layout, API client setup (base URL from env, JWT storage/attachment). Shared components scaffold (seat grid cell, countdown timer, toast/error display) — no full flow logic yet."

## Clarifications

### Session 2026-09-25

- Q: Next.js language stack (JavaScript vs TypeScript)? → A: Option B - JavaScript (`.jsx` / `.js`)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Next.js App Router Shell & Responsive Navigation (Priority: P1) 🎯 MVP

As a ticketing website visitor, I want a modern, dark-themed Next.js App Router layout with a navigation header, brand logo, page routes (`/`, `/login`, `/register`, `/events`, `/orders`), and responsive container styling so that I can navigate across application pages seamlessly on desktop and mobile screens.

**Why this priority**: Establishes the foundational user interface framework, routing structure, and visual theme required before implementing interactive ticketing user flows.

**Independent Test**: Can be tested independently by navigating between `/`, `/login`, `/register`, `/events`, `/orders` in a browser and verifying that page layouts render cleanly with consistent header navigation and mobile responsive layout.

**Acceptance Scenarios**:

1. **Given** a user visiting any page, **When** the page loads, **Then** the global layout renders a responsive header with brand logo ("FrontRow"), navigation links (`Events`, `Orders`), and auth status indicator.
2. **Given** a screen size under 768px (mobile viewport), **When** viewed on a mobile device, **Then** navigation layout wraps gracefully without horizontal scrollbars or broken overflow.
3. **Given** global CSS tokens, **When** rendered, **Then** pages exhibit dark mode glassmorphism aesthetic, sleek color gradients, and typography adhering to web application design guidance.

---

### User Story 2 - Centralized API Client & JWT Token Infrastructure (Priority: P1) 🎯 MVP

As a frontend client application, I want a centralized HTTP API client configured with `NEXT_PUBLIC_API_URL` that manages JWT authentication tokens, automatically attaches `Authorization: Bearer <token>` headers to requests, and parses API error responses (`401 Unauthorized`, `409 Conflict`, `422 Validation Error`).

**Why this priority**: Mandated by Constitution Principle II. Ensures secure, decoupled communication between the Next.js frontend and Python FastAPI backend without hardcoded URLs or exposed secrets.

**Independent Test**: Can be tested independently by invoking API client methods (`api.get()`, `api.post()`) with and without an active JWT token and asserting that headers, base URL concatenation, and error exceptions behave as expected.

**Acceptance Scenarios**:

1. **Given** an environment configuration file (`.env.local`), **When** `NEXT_PUBLIC_API_URL` is set to `http://localhost:8000`, **Then** the API client constructs all HTTP request URLs using this base URL.
2. **Given** a stored JWT bearer token in client storage, **When** an authenticated API request is dispatched, **Then** the API client automatically attaches `Authorization: Bearer <token>` to outbound HTTP request headers.
3. **Given** an HTTP `409 Conflict` or `401 Unauthorized` response from the backend API, **When** processed by the client, **Then** the API client extracts error detail messages cleanly for UI presentation.

---

### User Story 3 - Shared UI Component Library Scaffold (Priority: P2)

As a frontend developer, I want modular, reusable JavaScript (`.jsx` / `.js`) UI components (`SeatGridCell`, `CountdownTimer`, `Toast`, `Navbar`) with status styling (`AVAILABLE`, `LOCKED`, `SOLD`, `SELECTED`), countdown interval logic, and toast notification overlays so that User Flows (Spec 6) can compose them effortlessly.

**Why this priority**: Provides isolated, testable visual building blocks for the seat map grid, hold lease timers, and error notifications.

**Independent Test**: Can be tested independently by rendering components in isolation and verifying prop-driven state changes (e.g. seat status color transitions, timer ticks, toast auto-dismiss).

**Acceptance Scenarios**:

1. **Given** a `SeatGridCell` component, **When** passed status `AVAILABLE`, `LOCKED`, `SOLD`, or `SELECTED`, **Then** it renders appropriate status colors, cursor styles, and hover micro-animations (e.g. green for AVAILABLE, amber for LOCKED, muted gray for SOLD, blue for SELECTED).
2. **Given** a `CountdownTimer` component initialized with 300 seconds, **When** active, **Then** it formats remaining time as `mm:ss`, turns red when $< 60$ seconds remain, and triggers `onExpire()` when reaching `00:00`.
3. **Given** a `Toast` notification component, **When** triggered with an error or success message, **Then** it displays an animated notification overlay with a close button and optional auto-dismiss timer.

---

### Edge Cases

- What happens if `NEXT_PUBLIC_API_URL` is missing from environment variables? The API client defaults to `http://localhost:8000` with a console warning.
- What happens if `localStorage` is unavailable (e.g. SSR or strict privacy mode)? The token manager falls back gracefully to in-memory state without crashing during server-side rendering.
- What happens if `CountdownTimer` receives a negative or zero initial timestamp? It immediately displays `00:00` and fires `onExpire()` once.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST maintain a Next.js App Router application in `frontend/` using JavaScript (`.jsx` / `.js`), React 18+, and Vanilla CSS design tokens.
- **FR-002**: System MUST define App Router pages and layout structure (`app/layout.js`, `app/page.js`, `app/login/page.js`, `app/register/page.js`, `app/events/page.js`, `app/events/[id]/page.js`, `app/orders/page.js`).
- **FR-003**: System MUST provide a centralized API client module (`lib/api.js` or `services/api.js`) loading `NEXT_PUBLIC_API_URL` from environment variables.
- **FR-004**: API client MUST manage JWT token persistence (`lib/auth.js`) and automatically attach `Authorization: Bearer <token>` to authenticated HTTP requests.
- **FR-005**: System MUST provide a `SeatGridCell` component (`components/SeatGridCell.js`) rendering seat number, price, and operational status (`AVAILABLE`, `LOCKED`, `SOLD`, `SELECTED`) with distinct color themes and hover effects.
- **FR-006**: System MUST provide a `CountdownTimer` component (`components/CountdownTimer.js`) formatting remaining hold seconds as `mm:ss`, displaying a warning visual state when $< 60$ seconds remain, and invoking an `onExpire` callback upon lease expiry.
- **FR-007**: System MUST provide a `Toast` notification overlay component (`components/Toast.js`) capable of rendering success notices and error alerts (e.g., HTTP `409 Conflict` lock contention messages).
- **FR-008**: System MUST provide a `Navbar` header navigation component (`components/Navbar.js`) rendering brand title, page links, and logged-in user state.

### Key Entities *(include if feature involves data)*

- **API Configuration**: Environment settings (`NEXT_PUBLIC_API_URL`, default `http://localhost:8000`).
- **Auth Session State**: Token string, user email, and expiration claims.
- **Seat Cell State**: Props `{ id, row, seatNumber, section, price, status, isSelected, onClick }`.
- **Timer State**: `{ expiresAt, onExpire }`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All Next.js pages (`/`, `/login`, `/register`, `/events`, `/orders`) render cleanly without console or hydration errors.
- **SC-002**: Centralized API client automatically attaches JWT bearer tokens to 100% of authenticated HTTP requests.
- **SC-003**: `SeatGridCell`, `CountdownTimer`, `Toast`, and `Navbar` components render state transitions in under 16ms (60 FPS visual smoothness).

## Assumptions

- Next.js 14 App Router and Node.js 18+ environment are available.
- `frontend/.env.example` provides default configuration (`NEXT_PUBLIC_API_URL=http://localhost:8000`).
- Pure Vanilla CSS (`app/globals.css` / CSS Modules) is used for maximum flexibility and rich dark glassmorphism styling without Tailwind dependency conflicts.
