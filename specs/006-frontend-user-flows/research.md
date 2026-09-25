# Technical Research: Frontend User Flows

**Feature Branch**: `006-frontend-user-flows`
**Date**: 2026-09-25

## 1. Authentication Flow & JWT Token State Sync

### Problem Statement
User authentication must support registration (`POST /api/v1/auth/register`) and login (`POST /api/v1/auth/login`). Upon acquiring a JWT token, the token must be saved to client storage (`lib/auth.js`), the Navbar header must dynamically update to display the user's email, and the user must be redirected to `/events`.

### Research Findings & Decision
- **Decision**: Implement form submission handlers in `frontend/app/login/page.js` and `frontend/app/register/page.js`:
  1. Call `api.post('/api/v1/auth/register', { email, password })` or `api.post('/api/v1/auth/login', { email, password })`.
  2. Save returned `access_token` via `setToken(data.access_token)` and user info via `setUser({ email })`.
  3. Dispatch a custom window event (`window.dispatchEvent(new Event('auth-change'))`) so that `Navbar.js` instantly re-renders auth state without requiring a full page refresh.
  4. Navigate to `/events` using `router.push('/events')`.
- **Error Handling**: Catch `ApiError` exceptions and display clear Toast banners (e.g., "Email already registered" or "Invalid email or password").

## 2. Real-Time Seat Map 4-Second Polling Architecture

### Problem Statement
The seat map page (`/events/[id]`) must display live seat statuses (`AVAILABLE`, `LOCKED`, `SOLD`) and background-poll `GET /api/v1/events/{id}/seats` every 4 seconds without resetting active user seat selections or causing screen flicker.

### Research Findings & Decision
- **Decision**: In `frontend/app/events/[id]/page.js`:
  - Fetch initial seat map on component mount.
  - Establish a 4-second polling loop via `setInterval(fetchSeats, 4000)`.
  - Maintain `selectedSeatIds` in local React state independently from the polled seat map array.
  - Update polled seat states in React state (`setSeats(data.seats)`). If a seat currently selected by the user transitions from `AVAILABLE` to `LOCKED` or `SOLD` on the server, automatically remove it from `selectedSeatIds` and show a warning Toast.
  - Clean up interval on component unmount (`clearInterval(intervalId)`).

## 3. Hold Acquisition, Lease Countdown & Checkout Flow

### Problem Statement
When a user clicks "Hold Seats", the app must acquire a hold (`POST /api/v1/events/{id}/holds`), display an active 5-minute `CountdownTimer`, and present a checkout panel. If hold acquisition fails due to lock contention (`409 Conflict`), the app must display a clear Toast error message.

### Research Findings & Decision
- **Decision**: In `frontend/app/events/[id]/page.js`:
  1. Verify user is authenticated (`isAuthenticated()`). If unauthenticated, show Toast ("Please log in to hold seats") and redirect to `/login`.
  2. Call `api.post('/api/v1/events/${id}/holds', { seat_ids: selectedSeatIds })`.
  3. Store returned `hold_id`, `expires_at`, and `seat_ids` in React state (`activeHold`).
  4. Render `CountdownTimer` initialized with `expiresAt={activeHold.expires_at}`.
  5. Render "Complete Checkout" button. On click, call `api.post('/api/v1/checkout/holds/${activeHold.hold_id}', { payment_token: 'mock_token_ok' })`.
  6. On successful checkout, clear active hold state, display Toast success banner ("Checkout Successful!"), and redirect to `/orders`.
  7. On `ApiError` (e.g. 409 Conflict), clear selection, show Toast error banner, and refresh seat map.

## 4. AI Seat Search & Candidate Highlighting Flow

### Problem Statement
Users can enter natural language queries (e.g. "2 seats together under $150") in an AI search bar on the seat map page.

### Research Findings & Decision
- **Decision**: In `frontend/app/events/[id]/page.js`:
  1. Render AI search input box and "Search with AI" button.
  2. Call `api.post('/api/v1/events/${id}/ai-search', { query: searchText })`.
  3. Inspect returned `AISearchResponse`:
     - If `recommended_seat_ids` is non-empty, set `selectedSeatIds` to `recommended_seat_ids` and show Toast info ("AI recommended candidate seats highlighted!").
     - If `fallback_to_manual` is true or `recommended_seat_ids` is empty, show Toast info ("AI recommendation unavailable or no exact match found. Please select seats manually on the grid.").

## 5. Orders & Tickets History Flow

### Problem Statement
Authenticated users must be able to view their past orders and tickets on `/orders`.

### Research Findings & Decision
- **Decision**: In `frontend/app/orders/page.js`:
  1. Check authentication on mount. If unauthenticated, redirect to `/login`.
  2. Call `api.get('/api/v1/orders')`.
  3. Render order cards detailing Order ID, purchase timestamp, total amount, and individual ticket badges (Row, Seat Number, Price Paid).
  4. Render clean empty state if zero orders exist.
