# Implementation Plan: Frontend Skeleton & Dependencies

**Branch**: `005-frontend-skeleton-dependencies` | **Date**: 2026-09-25 | **Spec**: [specs/005-frontend-skeleton-dependencies/spec.md](file:///d:/projects/interviews/FrontRow-event-ticketing/specs/005-frontend-skeleton-dependencies/spec.md)

**Input**: Feature specification from `/specs/005-frontend-skeleton-dependencies/spec.md`

## Summary

The Frontend Skeleton & Dependencies feature establishes the Next.js App Router application foundation in `frontend/` using JavaScript (`.jsx` / `.js`), React 18, and Vanilla CSS design tokens. It provides the global glassmorphism layout, responsive navigation header (`Navbar.js`), page routing (`/`, `/login`, `/register`, `/events`, `/events/[id]`, `/orders`), centralized HTTP API client (`lib/api.js`), and JWT auth token manager (`lib/auth.js`). Additionally, it creates modular shared component scaffolds: `SeatGridCell.js` (rendering operational seat statuses `AVAILABLE`, `LOCKED`, `SOLD`, `SELECTED`), `CountdownTimer.js` (hold lease expiry countdown with `mm:ss` formatting and warning state), and `Toast.js` (notification & error overlay).

## Technical Context

**Language/Version**: JavaScript (Node.js 18+, React 18, Next.js 14 App Router)

**Primary Dependencies**: `next`, `react`, `react-dom`

**Storage**: `localStorage` (client-side JWT token storage with SSR in-memory fallback)

**Styling**: Pure Vanilla CSS (`app/globals.css` / CSS Modules) with CSS custom properties for dark mode glassmorphism, color tokens, and responsive breakpoints

**Testing**: React component rendering and manual browser routing verification

**Target Platform**: Web Browsers (Chrome, Firefox, Safari, Edge) & Mobile Viewports (< 768px)

**Project Type**: Next.js Web Application (`frontend/`)

**Performance Goals**: First Contentful Paint < 1.0s; 60 FPS component animations (< 16ms render phase)

**Constraints**: Pure JavaScript (`.js` / `.jsx`); pure Vanilla CSS (zero Tailwind dependencies); zero direct communication with database or LLM microservice (Principle II)

**Scale/Scope**: 1 web application frontend (`frontend/`), 5 App Router page routes, 1 API client module, 1 auth module, 4 shared UI component scaffolds

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Absolute Concurrency & Double-Selling Immunity)**: ✅ PASS. Frontend receives status error codes (`409 Conflict`) from Backend API and displays readable toast notifications; locking logic remains strictly server-side.
- **Principle II (Clean Architectural Separation & Security Boundaries)**: ✅ PASS. Frontend communicates strictly with Backend API (`NEXT_PUBLIC_API_URL`). Never communicates directly with LLM microservice or PostgreSQL DB. Auth identity managed strictly via JWT claims.
- **Principle III (Tri-Layer Lease Lifecycle Management)**: ✅ PASS. `CountdownTimer` component accepts `expiresAt` timestamp from backend hold response and triggers `onExpire` callback upon lease expiration.
- **Principle IV (Deterministic Candidate Seat Matching & AI Parsing Boundary)**: ✅ PASS. UI provides search prompt input and candidate seat recommendations list.
- **Principle V (Empirical Automated Concurrency Verification)**: ✅ PASS. Unaffected.
- **Principle VI (Mandatory Schema Validation)**: ✅ PASS. API client parses structured JSON error payloads (`401`, `409`, `422`).
- **Principle VII (Zero Secret Leakage)**: ✅ PASS. `NEXT_PUBLIC_API_URL` loaded safely via environment variables; `.env.example` committed with safe default `http://localhost:8000`.
- **Principle VIII (Strict Alembic Migrations)**: ✅ PASS. Unaffected.

## Project Structure

### Documentation (this feature)

```text
specs/005-frontend-skeleton-dependencies/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── frontend_routes.md# App Router page routing & navigation contract
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
frontend/
├── .env.example            # Environment template (NEXT_PUBLIC_API_URL=http://localhost:8000)
├── package.json            # Next.js 14, React 18, React DOM
├── next.config.js          # Next.js configuration
├── app/
│   ├── globals.css         # Design system tokens (colors, gradients, glassmorphism, typography)
│   ├── layout.js           # Root layout with Header/Navbar and Toast provider wrapper
│   ├── page.js             # Home page route / landing page
│   ├── login/
│   │   └── page.js         # Login page route scaffold
│   ├── register/
│   │   └── page.js         # Registration page route scaffold
│   ├── events/
│   │   ├── page.js         # Events catalog page route scaffold
│   │   └── [id]/
│   │       └── page.js     # Event seat map & details page route scaffold
│   └── orders/
│       └── page.js         # Orders & tickets history page route scaffold
├── components/
│   ├── Navbar.js           # Header navigation bar component
│   ├── SeatGridCell.js     # Visual seat item (AVAILABLE, LOCKED, SOLD, SELECTED)
│   ├── CountdownTimer.js   # Lease countdown timer (mm:ss format & <60s warning)
│   └── Toast.js            # Notification banner & error overlay component
└── lib/
    ├── api.js              # Centralized HTTP client (fetch API wrapper, error handling)
    └── auth.js             # Auth token manager (JWT storage in localStorage / SSR fallback)
```

**Structure Decision**: Standard Next.js App Router layout using JavaScript (`.js` / `.jsx`), pure Vanilla CSS (`app/globals.css`), and modular helpers in `lib/` and `components/`.

## Complexity Tracking

*No constitution violations present. All architectural decisions align strictly with Principles I–VIII.*
