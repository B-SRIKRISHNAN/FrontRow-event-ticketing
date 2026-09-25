# Technical Research: Frontend Skeleton & Dependencies

**Feature Branch**: `005-frontend-skeleton-dependencies`
**Date**: 2026-09-25

## 1. Vanilla CSS Design System & Glassmorphism Theme

### Problem Statement
The user experience must wow the user at first glance using curated color palettes, smooth gradients, subtle micro-animations, and modern typography without depending on external utility CSS frameworks (like Tailwind) that can introduce configuration bloat or dependency version conflicts.

### Research Findings & Decision
- **Decision**: Define a comprehensive CSS design token system in `frontend/app/globals.css` using CSS custom properties (`:root`):
  - **Color Palette**: Dark slate background (`#0b0f19`), deep indigo surface (`#111827`), glowing primary accent (`#6366f1` / `#4f46e5`), emerald green for `AVAILABLE` (`#10b981`), amber warning for `LOCKED` (`#f59e0b`), muted slate for `SOLD` (`#475569`), vibrant cyan for `SELECTED` (`#06b6d4`), and crimson red for errors (`#ef4444`).
  - **Glassmorphism Styling**: `background: rgba(17, 24, 39, 0.75)`, `backdrop-filter: blur(12px)`, subtle border `1px solid rgba(255, 255, 255, 0.1)`.
  - **Typography & Micro-Animations**: Inter/sans-serif font stack, smooth transition curves (`transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1)`), hover lift transforms (`transform: translateY(-2px)`).
- **Rationale**: Delivers a state-of-the-art, high-end visual aesthetic while keeping the codebase lightweight and dependency-free.

## 2. Centralized API Client & SSR-Safe Token Manager

### Problem Statement
Frontend requests to the Backend API (`NEXT_PUBLIC_API_URL`) must reliably include `Authorization: Bearer <token>` when authenticated, parse error responses (`401`, `409`, `422`), and handle server-side rendering (SSR) environments where `window.localStorage` is undefined.

### Research Findings & Decision
- **Decision**:
  1. **Token Manager (`lib/auth.js`)**:
     - Exports `getToken()`, `setToken(token)`, `removeToken()`, `getUser()`, `setUser(user)`.
     - Checks `typeof window !== 'undefined'` before accessing `localStorage`.
     - Maintains in-memory fallback state during SSR execution.
  2. **API Client (`lib/api.js`)**:
     - Wraps native `fetch` API.
     - Automatically prepends `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).
     - Reads JWT token from `lib/auth.js` and attaches `Authorization: Bearer <token>` if present.
     - Parses JSON response; if `!response.ok`, throws a custom `ApiError` class containing status code, detail message, and raw payload.
- **Rationale**: Centralizes all networking and error handling in one reusable module, preventing code duplication across Next.js pages.

## 3. Shared Component Library Scaffold (`.jsx` / `.js`)

### Problem Statement
User Flows (Spec 6) require modular, reusable components for seat map grid cells, hold lease countdown timers, navigation headers, and toast alerts.

### Research Findings & Decision
- **Decision**: Implement 4 core component scaffolds in `frontend/components/`:
  1. **`Navbar.js`**: Header bar rendering brand logo, navigation links (`Events`, `Orders`), auth button (`Login` / `Logout`), and logged-in user email badge.
  2. **`SeatGridCell.js`**: Visual seat cell component rendering row, seat number, price, and operational status (`AVAILABLE`, `LOCKED`, `SOLD`, `SELECTED`) with interactive click events and status-specific CSS classes.
  3. **`CountdownTimer.js`**: Receives `expiresAt` or `initialSeconds`. Calculates remaining time every second using `setInterval`. Renders formatted string `mm:ss`, applies a warning pulse animation when $< 60$s remain, and fires `onExpire()` when reaching 0.
  4. **`Toast.js`**: Notification banner overlay receiving `message`, `type` (`"success" | "error" | "info"`), and `onClose`. Includes optional auto-dismiss timer (default 4000ms).
- **Rationale**: Isolates component presentation and micro-interactions, making Spec 6 page integration fast and bug-free.

## 4. Next.js App Router Page Routing Structure

### Problem Statement
The application requires a clean, accessible page layout hierarchy for public and authenticated routes.

### Research Findings & Decision
- **Decision**: Structure `frontend/app/` into 5 page routes:
  - `app/layout.js`: Global root layout embedding `Navbar.js` and CSS design system.
  - `app/page.js`: Landing page redirecting or showcasing featured events.
  - `app/login/page.js`: User login page scaffold.
  - `app/register/page.js`: User registration page scaffold.
  - `app/events/page.js`: Events list catalog page scaffold.
  - `app/events/[id]/page.js`: Event seat map & AI seat search page scaffold.
  - `app/orders/page.js`: User order history and tickets page scaffold.
- **Rationale**: Strictly adheres to Next.js 14 App Router conventions.
