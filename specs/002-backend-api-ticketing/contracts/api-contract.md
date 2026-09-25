# OpenAPI / REST Interface Contract: Core Backend API (Ticketing)

**Feature**: `002-backend-api-ticketing` | **Date**: 2026-09-25

## 1. Authentication Endpoints

### `POST /auth/register`
- **Description**: Register a new user account.
- **Request Body**: `UserRegisterRequest` (`email`, `password`)
- **Response**: `201 Created` $\rightarrow$ `TokenResponse` (`access_token`, `token_type`)
- **Error Responses**:
  - `400 Bad Request`: Email already registered.

### `POST /auth/login`
- **Description**: Authenticate registered user and issue JWT bearer token.
- **Request Body**: `UserLoginRequest` (`email`, `password`)
- **Response**: `200 OK` $\rightarrow$ `TokenResponse` (`access_token`, `token_type`)
- **Error Responses**:
  - `401 Unauthorized`: Invalid credentials.

---

## 2. Event & Seat Map Endpoints

### `GET /events`
- **Description**: Retrieve active event catalog.
- **Headers**: None required (public endpoint).
- **Response**: `200 OK` $\rightarrow$ `list[EventResponse]`

### `GET /events/{id}/seats`
- **Description**: Retrieve seat map for a specified event with dynamic lazy expiration on read.
- **Headers**: None required (public endpoint).
- **Response**: `200 OK` $\rightarrow$ `SeatMapResponse` (`event_id`, `seats: list[SeatResponse]`)
- **Behavior**: Project seats with `status = 'LOCKED'` and `holds.expires_at < NOW()` as `status = 'AVAILABLE'`.

---

## 3. Hold Acquisition & Release Endpoints

### `POST /events/{id}/holds`
- **Description**: Temporarily lock requested seats for 5 minutes under strict row-locking transaction.
- **Headers**: `Authorization: Bearer <JWT>` (Required)
- **Request Body**: `HoldCreateRequest` (`seat_ids: list[int]`)
- **SQL Execution**: Bypasses ORM. Uses `text()` with `ORDER BY id ASC`, `LEFT JOIN holds h ON s.current_hold_id = h.id`, `WHERE s.event_id = :event_id AND s.id IN (...) FOR UPDATE OF s NOWAIT`.
- **Response**: `201 Created` $\rightarrow$ `HoldResponse` (`hold_id`, `event_id`, `seat_ids`, `status`, `created_at`, `expires_at`)
- **Error Responses**:
  - `401 Unauthorized`: Missing or invalid JWT.
  - `409 Conflict`: Seat already locked/sold, PostgreSQL lock error `55P03`, or seat count mismatch.

### `DELETE /holds/{hold_id}`
- **Description**: Explicitly release an active hold before expiration.
- **Headers**: `Authorization: Bearer <JWT>` (Required)
- **Response**: `200 OK` $\rightarrow$ `{ "message": "Hold released successfully" }`
- **Error Responses**:
  - `401 Unauthorized`: Missing or invalid JWT.
  - `403 Forbidden`: Hold belongs to a different user.
  - `404 Not Found`: Hold does not exist or is already completed/expired.

---

## 4. Checkout & Order Endpoints

### `POST /holds/{hold_id}/checkout`
- **Description**: Complete payment for an active hold, mark seats `SOLD`, set hold `COMPLETED`, and generate order/tickets.
- **Headers**: `Authorization: Bearer <JWT>` (Required)
- **Request Body**: `CheckoutRequest` (`payment_token: str`)
- **Behavior**:
  1. Call `process_mock_payment()`.
  2. Execute raw SQL conditional seat update `UPDATE seats SET status = 'SOLD' WHERE current_hold_id = :hold_id AND status = 'LOCKED'`.
  3. If updated rows == hold seat count and `expires_at >= NOW()`: set hold status `COMPLETED`, create `orders` & `tickets` records, commit.
  4. If zero rows updated: rollback DB, set hold status `EXPIRED`, trigger `process_mock_refund()`, return `409 Conflict`.
- **Response**: `200 OK` $\rightarrow$ `OrderResponse` (`id`, `user_id`, `total_amount`, `created_at`, `tickets`)
- **Error Responses**:
  - `401 Unauthorized`: Missing/invalid JWT.
  - `409 Conflict`: Hold expired or invalid for checkout (triggers mock refund callback).

### `GET /orders`
- **Description**: Retrieve order history for the authenticated customer.
- **Headers**: `Authorization: Bearer <JWT>` (Required)
- **Response**: `200 OK` $\rightarrow$ `list[OrderResponse]`
- **Behavior**: Filter orders strictly by JWT user ID claim (`sub`).

---

## 5. AI Search Endpoint (Stub Contract)

### `POST /events/{id}/ai-search`
- **Description**: Parse natural language query into candidate seat preferences (Spec 4 stub).
- **Request Body**: `AISearchRequest` (`query: str`)
- **Response**: `200 OK` $\rightarrow$ `AISearchResponse` (`quantity`, `adjacency`, `max_price`, `preferred_section`, `recommended_seat_ids`)
