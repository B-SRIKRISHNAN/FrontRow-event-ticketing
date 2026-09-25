# Implementation Plan: Frontend User Flows

**Branch**: `006-frontend-user-flows` | **Date**: 2026-09-25 | **Spec**: [specs/006-frontend-user-flows/spec.md](file:///d:/projects/interviews/FrontRow-event-ticketing/specs/006-frontend-user-flows/spec.md)

**Input**: Feature specification from `/specs/006-frontend-user-flows/spec.md`

## Summary

The Frontend User Flows feature delivers the complete end-to-end user experience for the FrontRow ticketing platform across 5 primary flows: (1) Authentication Flow (`/register` & `/login` form processing, JWT bearer token persistence, and Navbar state updates), (2) Event Catalog & Real-Time Seat Map Polling Flow (`/events` catalog list and `/events/[id]` seat map with 4-second background polling), (3) Seat Selection, Hold Lease, Countdown Timer & Checkout Flow (interactive seat picking, `POST /holds` hold lease acquisition, 5-minute `CountdownTimer` display, mock payment checkout, and `409 Conflict` lock contention handling), (4) Order History & Ticket Receipt Flow (`/orders` purchase history and ticket badges), and (5) AI Natural Language Seat Search & Manual Fallback Flow (`POST /ai-search` candidate seat highlighting and manual selection Toast advice).

## Technical Context

**Language/Version**: JavaScript (Node.js 18+, React 18, Next.js 14 App Router)

**Primary Dependencies**: `next`, `react`, `react-dom`

**Storage**: `localStorage` (JWT bearer token & user session state via `lib/auth.js`)

**Styling**: Pure Vanilla CSS (`app/globals.css`) with CSS custom properties for dark mode glassmorphism, status colors, and responsive layouts

**Backend API Integration**: `lib/api.js` calling Python FastAPI Backend (`http://localhost:8000`) and LLM Engine (`http://localhost:8001`)

**Target Platform**: Web Browsers (Chrome, Firefox, Safari, Edge) & Mobile Viewports (< 768px)

**Project Type**: Next.js Web Application (`frontend/`)

**Performance Goals**: Flow completion < 2 minutes; 4-second seat map polling without UI flicker; 60 FPS seat selection rendering

**Constraints**: Pure JavaScript (`.jsx` / `.js`); pure Vanilla CSS (zero Tailwind dependencies); zero direct DB or LLM calls (Principle II decoupled client RPC)

**Scale/Scope**: 5 App Router page routes (`/register`, `/login`, `/events`, `/events/[id]`, `/orders`), 4-second seat map polling, 5-minute lease timer

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Absolute Concurrency & Double-Selling Immunity)**: ✅ PASS. Hold acquisition (`POST /events/{id}/holds`) and checkout (`POST /checkout/holds/{holdId}`) execute against backend atomic ACID transactions. Lock contention (`409 Conflict`) displays Toast error banners and resets UI.
- **Principle II (Clean Architectural Separation & Security Boundaries)**: ✅ PASS. Frontend communicates strictly via HTTP REST to Backend API (`lib/api.js`). User identity derived strictly from verified JWT bearer claims.
- **Principle III (Tri-Layer Lease Lifecycle Management)**: ✅ PASS. Seat map view displays `AVAILABLE` seats via lazy read expiration. Hold lease UI displays `CountdownTimer` initialized from backend `expires_at` timestamp.
- **Principle IV (Deterministic Candidate Seat Matching & AI Parsing Boundary)**: ✅ PASS. AI search bar calls `POST /events/{id}/ai-search`, automatically highlights returned candidate seat IDs, and falls back to manual selection advice if `fallback_to_manual=True`.
- **Principle V (Empirical Automated Concurrency Verification)**: ✅ PASS. End-to-end user flows verified against backend integration test suite.
- **Principle VI (Mandatory Schema Validation)**: ✅ PASS. `lib/api.js` handles structured API request/response payloads and error exceptions.
- **Principle VII (Zero Secret Leakage)**: ✅ PASS. `NEXT_PUBLIC_API_URL` loaded via environment variables; `.env.example` committed with safe default `http://localhost:8000`.
- **Principle VIII (Strict Alembic Migrations)**: ✅ PASS. Unaffected.

## Project Structure

### Documentation (this feature)

```text
specs/006-frontend-user-flows/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── user_flow_contracts.md # End-to-end page flow API contract mapping
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── globals.css         # Dark glassmorphism CSS design system
│   ├── layout.js           # Root layout with Navbar and Toast container
│   ├── page.js             # Landing page with hero & CTA links
│   ├── login/
│   │   └── page.js         # User login form flow & JWT auth submission
│   ├── register/
│   │   └── page.js         # User registration form flow & account creation
│   ├── events/
│   │   ├── page.js         # Events catalog listing page (GET /api/v1/events)
│   │   └── [id]/
│   │       └── page.js     # Interactive seat map, 4s polling, AI search, hold & checkout
│   └── orders/
│       └── page.js         # Confirmed user orders & tickets history (GET /api/v1/orders)
├── components/
│   ├── Navbar.js           # Header navigation & auth state badge
│   ├── SeatGridCell.js     # Seat cell item (AVAILABLE, LOCKED, SOLD, SELECTED)
│   ├── CountdownTimer.js   # Lease countdown timer (mm:ss format & <60s warning)
│   └── Toast.js            # Notification banner & error alert overlay
└── lib/
    ├── api.js              # Centralized HTTP client (fetch API wrapper, error handling)
    └── auth.js             # Auth token & session manager (localStorage / SSR safety)
```

**Structure Decision**: Complete Next.js 14 App Router application in `frontend/` executing end-to-end user flows against FastAPI Backend (`http://localhost:8000`).

## Complexity Tracking

*No constitution violations present. All architectural decisions align strictly with Principles I–VIII.*
