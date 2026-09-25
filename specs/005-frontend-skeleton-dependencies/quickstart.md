# Quickstart & Validation Guide: Frontend Skeleton & Dependencies

**Feature Branch**: `005-frontend-skeleton-dependencies`
**Date**: 2026-09-25

This guide provides runnable commands to launch the Next.js frontend dev server and validate page routing, component scaffolds, and API client setup.

---

## Prerequisites

1. **Working Directory**: Open terminal in `frontend/`:
   ```powershell
   cd d:\projects\interviews\FrontRow-event-ticketing\frontend
   ```
2. **Environment Setup**: Ensure `frontend/.env.local` or `frontend/.env.example` contains:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

---

## Scenario 1: Start Next.js Development Server

Launch the Next.js App Router dev server on port 3000:

```powershell
npm run dev
```

Open your browser at `http://localhost:3000`.

---

## Scenario 2: Validate App Router Route Navigation

Verify that all 5 page routes load cleanly without console or hydration errors:

1. **Home Landing Page**: Navigate to `http://localhost:3000/`
2. **Login Page**: Navigate to `http://localhost:3000/login`
3. **Register Page**: Navigate to `http://localhost:3000/register`
4. **Events Catalog**: Navigate to `http://localhost:3000/events`
5. **Orders History**: Navigate to `http://localhost:3000/orders`

---

## Scenario 3: Validate Shared Component Scaffolds

Inspect component rendering in browser dev tools:
- **`Navbar`**: Renders glassmorphism background, logo ("FrontRow"), links, and login button.
- **`SeatGridCell`**: Displays seat status styling:
  - `AVAILABLE` -> Emerald green theme with hover glow
  - `LOCKED` -> Amber warning theme
  - `SOLD` -> Muted slate theme
  - `SELECTED` -> Cyan active theme
- **`CountdownTimer`**: Displays `mm:ss` countdown timer, turns red when $< 60$s.
- **`Toast`**: Renders top-right animated alert banner.
