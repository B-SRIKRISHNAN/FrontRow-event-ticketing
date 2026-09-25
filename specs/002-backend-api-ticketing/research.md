# Research & Technical Decisions: Core Backend API (Ticketing)

**Feature**: `002-backend-api-ticketing` | **Date**: 2026-09-25

## 1. Concurrency Locking & Raw SQL Execution Architecture

### Decision
All concurrency-critical operations (`POST /events/{id}/holds`, background sweeper worker, and `POST /holds/{hold_id}/checkout`) will be executed using raw parameterized SQL strings via `sqlalchemy.text()` executed directly on the `AsyncConnection` / `AsyncSession` execution path (`await session.execute(text(...))`), completely bypassing the ORM query builder. All non-concurrency-critical operations (`GET /events`, `GET /events/{id}/seats`, `GET /orders`, user authentication lookups) will use standard SQLAlchemy 2.0 ORM query patterns.

### Rationale
- **Non-blocking row-level lock scoping**: High-concurrency seat locking requires exact control over locking syntax (`SELECT ... FROM seats s LEFT JOIN holds h ON s.current_hold_id = h.id WHERE s.event_id = :event_id AND s.id IN (...) ORDER BY s.id ASC FOR UPDATE OF s NOWAIT`). Scoping locking strictly to alias `s` (`FOR UPDATE OF s`) prevents PostgreSQL from placing row or table locks on the joined `holds` table.
- **Deadlock Immunity**: Sorting seat IDs ascending (`ORDER BY s.id ASC`) in multi-seat hold requests enforces a strict lock order across concurrent transactions.
- **Immediate Contention Resolution**: Using `NOWAIT` causes PostgreSQL to throw error code `55P03` (`lock_not_available`) immediately when a seat is held by an uncommitted concurrent transaction, allowing the API to return HTTP `409 Conflict` within 2-5ms without blocking worker threads.

### Alternatives Considered
- **SQLAlchemy ORM `.with_for_update(nowait=True, of=Seat)`**: Rejected for concurrency-critical queries because SQLAlchemy ORM query generation introduces minor overhead and complex `LEFT JOIN` alias compilation that can lead to unintended lock propagation on joined entities under high concurrency.

---

## 2. Database Connection Pooling Strategy

### Decision
- **Primary Request Pool**: Create a dedicated SQLAlchemy `create_async_engine` instance configured with `pool_size=15`, `max_overflow=10`, `pool_timeout=30`, `pool_pre_ping=True`, `pool_recycle=1800`.
- **Sweeper Worker Pool**: Create an isolated, separate `create_async_engine` instance configured with `pool_size=2`, `max_overflow=1`, `pool_pre_ping=True` dedicated exclusively to the background lease sweeper worker task.

### Rationale
- Sizing the primary connection pool to 15 (with +10 overflow) ensures that automated concurrency collision tests running 10-15+ simultaneous requests on identical seats complete instantly without connection starvation or pooling wait timeouts.
- Isolating the background sweeper worker onto a separate small connection pool prevents background cleanup jobs from consuming request-serving connections during peak traffic spikes.

---

## 3. JWT Authentication & Claims-Based User Identity

### Decision
Authentication will use JWT bearer tokens signed with HMAC-SHA256 (`HS256`). Passwords will be hashed using `bcrypt` (via `passlib` or `argon2`/`bcrypt`). The FastAPI dependency `get_current_user` will extract and decode the HTTP Authorization header (`Bearer <token>`), verify the cryptographic signature, and return the authenticated `User` entity.

### Rationale
- Enforces Constitution Principle II: User identity for all hold, release, checkout, and order endpoints is derived strictly from verified JWT claims (`sub`), never from client-supplied request body or query parameters (`user_id`).

---

## 4. Tri-Layer Lease Lifecycle & Sweeper Strategy

### Decision
Enforce seat lease expiration across three redundant layers (Constitution Principle III):
1. **Lazy Expiration on Read (`GET /events/{id}/seats`)**: Query checks `(s.status = 'LOCKED' AND h.expires_at < NOW())` and projects projected status as `AVAILABLE` without write database locks.
2. **Lazy Overwrite on Lock (`POST /events/{id}/holds`)**: Hold acquisition locking query evaluates `(s.status = 'AVAILABLE' OR (s.status = 'LOCKED' AND h.expires_at < NOW()))` inside the atomic locking transaction.
3. **Asynchronous Sweeper Worker**: Background `asyncio` worker running every 15–30s executes:
   ```sql
   SELECT id FROM holds WHERE status = 'ACTIVE' AND expires_at < NOW() FOR UPDATE SKIP LOCKED;
   ```
   For matched expired holds, sets `seats.status = 'AVAILABLE'`, `seats.current_hold_id = NULL`, and `holds.status = 'EXPIRED'` in a single transaction.

### Rationale
- `seats.current_hold_id` is only nulled upon lease expiration by the sweeper or release. Successful checkouts retain `current_hold_id` as a permanent reference to the creating hold.

---

## 5. Atomic Checkout & Mock Payment / Refund

### Decision
The checkout endpoint `POST /holds/{hold_id}/checkout` executes the following sequence:
1. Execute no-op mock payment function `process_mock_payment(amount, user_id)` which returns a mock payment reference token.
2. Open DB transaction. Execute conditional raw SQL update:
   ```sql
   UPDATE seats SET status = 'SOLD'
   WHERE current_hold_id = :hold_id AND status = 'LOCKED' AND id IN (
     SELECT seat_id FROM seats WHERE current_hold_id = :hold_id
   );
   ```
3. Check affected row count. If affected rows equal the expected count for the hold and `holds.expires_at >= NOW()`:
   - Set `holds.status = 'COMPLETED'` and `holds.order_id = :new_order_id`.
   - Create `orders` record and corresponding `tickets` records.
   - Commit transaction and return HTTP `200 OK`.
4. If zero rows updated (hold expired, released, or already checked out):
   - Roll back transaction.
   - Set `holds.status = 'EXPIRED'`.
   - Trigger `process_mock_refund(payment_ref)` stub.
   - Return HTTP `409 Conflict` with error message `"Hold expired or invalid for checkout"`.

### Rationale
- Fulfills Constitution Principle I (Atomic Checkout): Guarantees that if a hold expires or is stolen before payment completes, the payment is refunded immediately and no double-sold tickets or orphaned orders are created.

---

## 6. AI Search Endpoint & Fallback Contract

### Decision
Expose `POST /events/{id}/ai-search` accepting `{ "query": "string" }`. The endpoint validates the request payload and returns a Pydantic-validated JSON response containing:
```json
{
  "quantity": 2,
  "adjacency": true,
  "max_price": 150.00,
  "preferred_section": "A",
  "recommended_seat_ids": [1, 2]
}
```
For Spec 2, a deterministic matching stub parses the query or falls back to selecting available seats ordered by `row ASC, seat_number ASC`.

### Rationale
- Establishes the Pydantic-validated contract shape for AI candidate seat matching (Constitution Principle IV) while deferring actual LLM engine integration to Spec 4.
