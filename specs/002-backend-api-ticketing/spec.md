# Feature Specification: Core Backend API (Ticketing)

**Feature Branch**: `002-backend-api-ticketing`

**Created**: 2026-09-25

**Status**: Draft

**Input**: User description: "Spec 2 — Core Backend API (Ticketing) - Auth, DB engine & connection pooling, Events & seat map, Hold acquisition, Explicit release, Checkout, Orders, AI search shape/fallback contract, Asynchronous sweeper worker."

## Clarifications

### Session 2026-09-25

- Q: Are concurrency-critical queries (hold acquisition, sweeper, checkout) executed as raw SQL queries without ORM query builders? → A: YES. All concurrency-critical operations (hold acquisition, sweeper worker, checkout) MUST be written as raw parameterized SQL strings using SQLAlchemy `text()` executed directly on the connection/session, while non-critical endpoints (`GET /events`, `GET /orders`, user auth reads) use standard ORM patterns.
- Q: Is `FOR UPDATE` in hold acquisition explicitly scoped to the `seats` table / table alias (`FOR UPDATE OF seats NOWAIT` / `FOR UPDATE OF s NOWAIT`)? → A: YES. Row locking MUST explicitly specify `FOR UPDATE OF seats NOWAIT` (or `FOR UPDATE OF s NOWAIT` when `seats s` is aliased) so that row locks are placed strictly on the targeted `seats` table/alias and NEVER lock the joined `holds` table.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Authentication & Identity Protection (Priority: P1) 🎯 MVP

As a ticketing platform customer, I want to securely register an account and log in so that my identity is verified via encrypted tokens for all reservation and purchase transactions.

**Why this priority**: Core security foundation. All seat holding, releasing, and order creation require authenticated user identity derived exclusively from cryptographically signed claims (Constitution Principle II).

**Independent Test**: Can be tested independently by sending registration and login requests to retrieve JWT bearer tokens, followed by authenticating requests using the token claims.

**Acceptance Scenarios**:

1. **Given** a new customer with a unique email and password, **When** they submit account registration details, **Then** the system registers the user and returns an encrypted JWT authentication token.
2. **Given** an existing customer with registered credentials, **When** they log in with correct email and password, **Then** the system issues a valid JWT access token containing their verified user identity.
3. **Given** an unauthenticated request or an invalid/expired token attempting to reserve seats or view orders, **Then** the system rejects the request with HTTP `401 Unauthorized`.

---

### User Story 2 - Event Discovery & Real-Time Seat Map Browsing (Priority: P1) 🎯 MVP

As a event attendee, I want to view available events and inspect real-time seat availability maps with automatic expiry calculation so that I can pick the best available seats without seeing stale hold states.

**Why this priority**: Core user journey for discovering show times and picking seats before starting checkout.

**Independent Test**: Can be tested independently by querying event details and seat maps for an event, verifying seat pricing, row letters, seat numbers, and dynamic lazy expiration of expired locks.

**Acceptance Scenarios**:

1. **Given** active events in the catalog, **When** a user requests the event list, **Then** the system returns event titles, descriptions, venue names, and show times.
2. **Given** an event seat map with seats whose hold lease has expired (`holds.expires_at < NOW()`), **When** a user requests seat details, **Then** the system dynamically calculates and returns those expired seats as `AVAILABLE` without write database locks (lazy expiration on read).
3. **Given** an event seat map, **When** a user polls seat states every 4 seconds, **Then** the system returns exact seat statuses (`AVAILABLE`, `LOCKED`, `SOLD`), section pricing, and hold lease timestamps.

---

### User Story 3 - Atomic Concurrency-Safe Seat Hold Acquisition (Priority: P1) 🎯 MVP

As a customer buying tickets for a popular show, I want to temporarily hold one or more selected seats for 5 minutes so that no other buyer can double-book them while I am entering payment details.

**Why this priority**: Absolute concurrency guarantee and double-selling immunity (Constitution Principle I). Guarantees ultra-short database locks (~2-5ms) with zero deadlocks and immediate contention resolution.

**Independent Test**: Can be tested independently by submitting single and multi-seat hold requests under high concurrent load (10+ simultaneous requests for the exact same seat) and verifying exactly 1 request succeeds while $N-1$ receive HTTP `409 Conflict`.

**Acceptance Scenarios**:

1. **Given** one or more available seats for an event, **When** an authenticated customer requests a 5-minute hold, **Then** the system locks the requested seats in ascending ID order, creates an active hold record (`status = 'ACTIVE'`, 5-minute expiry), marks seats as `LOCKED`, and returns the hold identifier.
2. **Given** multiple customers simultaneously attempting to hold the exact same seat at the exact same millisecond, **When** lock acquisition runs, **Then** the system uses non-blocking row locking (`SELECT FOR UPDATE OF seats NOWAIT`), allowing exactly 1 customer to acquire the hold while immediately returning HTTP `409 Conflict` to all competing requests.
3. **Given** a multi-seat hold request where at least one requested seat is already locked or unavailable, **When** hold acquisition is executed, **Then** the system performs an all-or-nothing transaction rollback, leaving all seats untouched and returning HTTP `409 Conflict`.

---

### User Story 4 - Atomic Checkout & Order Completion (Priority: P1) 🎯 MVP

As a customer holding reserved seats, I want to complete checkout so that my payment is processed, seats are permanently marked `SOLD`, and a confirmed order with tickets is generated.

**Why this priority**: Completes the purchasing lifecycle and converts temporary holds into final ticket orders with double-selling immunity.

**Independent Test**: Can be tested independently by taking an active hold, completing mock payment, verifying seats transition to `SOLD`, hold transitions to `COMPLETED` linked to `order_id`, and tickets are generated.

**Acceptance Scenarios**:

1. **Given** an active hold owned by the authenticated customer, **When** checkout is submitted before hold expiration, **Then** the system executes mock payment, updates seats to `SOLD`, sets hold status to `COMPLETED` with the new `order_id`, creates the order and ticket records, and returns HTTP `200 OK` with order details.
2. **Given** a hold that expires or is stolen before payment completes, **When** checkout is attempted, **Then** zero seat rows are updated, the transaction rolls back, hold status is marked `EXPIRED`, HTTP `409 Conflict` is returned, and a mock refund is issued for any processed payment.
3. **Given** an authenticated customer with completed purchases, **When** they request their order history (`GET /orders`), **Then** the system returns their past orders with total amounts, seat details, and purchase timestamps derived from their verified JWT identity.

---

### User Story 5 - Explicit Hold Release (Priority: P2)

As a customer who changes their mind after holding seats, I want to explicitly release my active hold so that the seats instantly become available for other buyers without waiting for lease timeout.

**Why this priority**: Improves venue seat availability and user experience by unlocking canceled holds immediately.

**Independent Test**: Can be tested independently by calling `DELETE /holds/{hold_id}` with the owner's JWT token, verifying seats return to `AVAILABLE` status.

**Acceptance Scenarios**:

1. **Given** an active hold owned by the authenticated user, **When** the user explicitly releases the hold, **Then** the system verifies JWT ownership, sets hold status to `EXPIRED`, nulls `current_hold_id` on associated seats, resets seat status to `AVAILABLE`, and returns HTTP `200 OK`.
2. **Given** a user attempting to release a hold belonging to a different user, **When** the release request is processed, **Then** the system rejects the operation with HTTP `403 Forbidden` or `404 Not Found`.

---

### User Story 6 - Asynchronous Lease Sweeper & Natural Language AI Search Stub (Priority: P3)

As a system administrator, I want an automated background sweeper worker to recycle expired holds and an AI search fallback contract so that seat inventory stays clean and AI discovery is ready for integration.

**Why this priority**: Provides background housekeeping (Constitution Principle III) and establishes the contract interface for future AI semantic search integration (Spec 4).

**Independent Test**: Can be tested independently by allowing holds to pass `expires_at`, running the sweeper cycle, and verifying seats transition back to `AVAILABLE`.

**Acceptance Scenarios**:

1. **Given** expired active holds (`expires_at < NOW()`), **When** the background sweeper worker executes on its 15–30s interval, **Then** it locks expired holds using `SKIP LOCKED`, sets seat statuses to `AVAILABLE`, nulls `current_hold_id`, and marks hold statuses as `EXPIRED` in a single transaction.
2. **Given** a natural language seat query sent to `POST /events/{id}/ai-search`, **When** the endpoint is invoked, **Then** it validates the query shape and returns a structured candidate seat preference response using a graceful fallback contract.

---

### Edge Cases

- What happens if a database transaction times out during hold acquisition? The database connection rolls back immediately, releasing all temporary locks and returning HTTP `409 Conflict`.
- What happens if 15+ concurrent requests hit the API simultaneously? The SQLAlchemy connection pool (sized $\ge 15$ with overflow) accommodates concurrent request execution without connection starvation or pooling timeouts.
- What happens if the sweeper worker runs while a user is attempting to purchase an expired hold? The atomic checkout condition checks `holds.expires_at >= NOW()`; if swept first, checkout updates 0 rows, rolls back, returns `409 Conflict`, and triggers mock refund stub.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide user registration (`POST /auth/register`) and login (`POST /auth/login`) returning JWT bearer tokens.
- **FR-002**: System MUST enforce user identity for all hold, release, checkout, and order operations strictly from verified JWT claims (Constitution Principle II).
- **FR-003**: System MUST configure a dedicated SQLAlchemy async engine with explicit connection pool sizing (base pool $\ge 15$, overflow $\ge 10$, `pool_pre_ping=True`) for request processing, and an isolated separate connection pool for the background sweeper worker.
- **FR-004**: System MUST expose `GET /events` and `GET /events/{id}/seats` endpoints with dynamic lazy-expiry calculation returning seat availability without DB write operations.
- **FR-005**: System MUST execute hold acquisition (`POST /events/{id}/holds`) using raw parameterized SQL (`text()`) directly on the connection/session with `ORDER BY id ASC`, `LEFT JOIN` from `seats s` to `holds h`, `SELECT ... FOR UPDATE OF s NOWAIT` (explicitly scoped to the `seats` table/alias `s`), availability predicate evaluation, and explicit row count validation, returning HTTP `409 Conflict` on error `55P03` or count mismatch (Constitution Principle I).
- **FR-006**: System MUST execute atomic checkout (`POST /holds/{hold_id}/checkout`) using raw parameterized SQL with mock payment execution, conditional seat update (`status = 'SOLD'` where `current_hold_id = :hold_id` and `expires_at >= NOW()`), hold status update to `COMPLETED`, order/ticket creation, and automatic mock refund on zero-row update failure.
- **FR-007**: System MUST provide explicit hold release (`DELETE /holds/{hold_id}`) with strict JWT ownership verification.
- **FR-008**: System MUST provide customer order history retrieval (`GET /orders`) filtered by the caller's JWT user ID.
- **FR-009**: System MUST run an asynchronous background lease sweeper worker on a 15–30 second interval querying expired holds with `SKIP LOCKED` to recycle seats to `AVAILABLE` state (Constitution Principle III).
- **FR-010**: System MUST expose an AI search endpoint contract (`POST /events/{id}/ai-search`) returning Pydantic-validated structured seat preferences with fallback support for unparsed or empty queries.
- **FR-011**: System MUST enforce Pydantic schema validation across all request payloads and response DTOs (Constitution Principle VI).

### Key Entities *(include if feature involves data)*

- **User (`users`)**: Represents registered customers (`id`, `email`, `hashed_password`, `created_at`).
- **Event (`events`)**: Represents ticketing events (`id`, `title`, `description`, `venue_name`, `show_time`, `created_at`).
- **Seat (`seats`)**: Physical seat records (`id`, `event_id`, `row`, `seat_number`, `section`, `price`, `status`, `current_hold_id`).
- **Hold (`holds`)**: Reservation lease (`id` UUID, `user_id`, `event_id`, `status`, `created_at`, `expires_at`, `order_id`).
- **Order & Ticket (`orders`, `tickets`)**: Confirmed purchase transactions (`orders`: `id`, `user_id`, `total_amount`, `created_at`; `tickets`: `id`, `order_id`, `seat_id`, `price_paid`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% immunity to double-selling under automated concurrency collision testing (10+ simultaneous requests for the exact same seat results in exactly 1 success and $N-1$ HTTP 409 Conflicts).
- **SC-002**: Database physical row locks during hold acquisition resolve in under 10ms without table-level blocking.
- **SC-003**: Seat map polling (`GET /events/{id}/seats`) responds in under 50ms under 4-second client polling.
- **SC-004**: Background sweeper worker recycles expired holds within 30 seconds of lease expiration without blocking active checkouts.
- **SC-005**: 100% of API endpoints validate request/response payloads using Pydantic schemas.

## Assumptions

- PostgreSQL database is initialized with Spec 1 schema migrations applied.
- `DATABASE_URL` and JWT secret configuration are loaded from `backend/.env`.
- Mock payment stub always succeeds on first invocation and triggers a mock refund callback if checkout transaction fails post-payment.
- Logical hold duration defaults to 300 seconds (5 minutes) unless overridden by environment configuration.
