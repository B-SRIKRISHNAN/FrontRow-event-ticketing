# System Constitution & Architectural Blueprint: FrontRow

## 1. System Vision & Scope
FrontRow is a seat-level event ticketing platform engineered to guarantee absolute correctness under high concurrency. The system enables users to view real-time seat states, temporarily lock seats for a checkout window, and purchase them without any risk of double-selling. It features an isolated, read-only LLM assistant microservice that parses natural language queries into structured preferences without making availability decisions.

---

## 2. Technology Stack & Operational Constraints

* **Frontend:** React / Next.js.
* **Backend API:** Python FastAPI (using an ORM / SQLAlchemy / asyncpg).
* **LLM Engine:** Python FastAPI microservice wrapping an abstracted LLM provider interface (implementation-agnostic — Gemini SDK, OpenAI SDK, LangChain, etc. are all valid; the provider must be swappable via configuration/env, not hardcoded to one SDK), with Pydantic for response validation.
* **Primary Database:** PostgreSQL (strictly leveraging ACID transactions and row-level locks).
* **Environment Configuration:** All credentials and API keys (including the LLM provider's API key) loaded via `.env` files. The logical hold duration (see 4.1) is also environment-configurable, not hardcoded.
* **Architecture Boundary:** Clean four-part separation: Frontend ↔ Backend API ↔ LLM Engine & PostgreSQL. The frontend never communicates directly with the LLM engine or the database.
* **Enhancements Out of Scope for MVP (Documented for Roadmap):** Redis distributed locks, WebSockets/SSE real-time streaming, Locust load testing frameworks, a cookie-based session upgrade (HttpOnly refresh token) beyond the MVP's plain JWT auth, and a finer-grained venue model (multiple sections within a row, non-uniform layouts, positional sub-preferences such as corner/center seats).

---

## 3. Core Domain Entities & Relational Rules

* **Users:** Authentication and order ownership (`users`).
* **Events:** Event metadata, venue details, and show timings (`events`).
* **Seats:** Individual bookable units tied to an event (`seats`). Each seat contains physical location (`row`, `seat_number`, `section`), `price`, operational `status` (`AVAILABLE`, `LOCKED`, `SOLD`), and a nullable reference to the active hold (`current_hold_id`). `section` is derived from (or set equal to) `row` for the POC layout (see 5.x) — it is not an independent axis. `seat_number` is scoped per row (resets at each row), not globally continuous across the venue; global uniqueness is provided solely by each seat's primary key `id`.
* **Holds:** Unique temporary lease reservations (`holds`). Represents the checkout session entity tracking `user_id`, `event_id`, lifecycle `status` (`ACTIVE`, `COMPLETED`, `EXPIRED`), creation time, `expires_at` (a 5-minute window, configurable via env), and a nullable `order_id` (see 4.4). A single hold can associate with multiple seats. `expires_at` lives only on `holds` — seats never carry their own expiry timestamp.
* **Orders & Tickets:** Confirmed transactions (`orders`, `tickets`) capturing finalized seat purchases post-checkout.

**Terminology note:** throughout this document, "lock" refers strictly to the short-lived physical database row lock (section 4.1), while "hold" refers to the 5-minute logical reservation represented by the `holds` table and the seat `status = 'LOCKED'`. These two terms are not interchangeable.

---

## 4. Concurrency & Seat Locking Engine (Core Constitution)

### 4.1. Physical vs. Logical Locking
* **Physical DB Lock Duration:** Ultra-short (~2ms to 5ms), bounded strictly inside an explicit database transaction block. Never keep a physical database lock or connection open while awaiting user input or payment.
* **Logical Lease Duration:** 5 minutes from hold initiation by default, configurable via environment variable. Tracked via `holds.expires_at`; the seat's `current_hold_id` links to the owning hold, but the expiry timestamp itself lives only on `holds`.

### 4.2. Atomic Hold Acquisition Rules
When a user requests a hold on one or more seats:
1. **Deterministic Ordering:** Input seat IDs must be ordered ascending (`ORDER BY id ASC`) to prevent circular deadlocks across concurrent group transactions.
2. **Join Construction:** The locking query must use a `LEFT JOIN` from `seats` to `holds` on `current_hold_id` — never an `INNER JOIN`, and never a comma-join with the equality condition placed in `WHERE`. An `AVAILABLE` seat has `current_hold_id = NULL` by definition; under an `INNER JOIN` (or its comma-join equivalent), such a seat matches zero rows in `holds` and is silently dropped from the result set entirely, before the availability predicate even runs — meaning a never-before-locked seat could never be acquired. `LEFT JOIN` preserves the seat row regardless of match, returning `holds.expires_at` as `NULL` when unmatched, which is harmless since the `AVAILABLE` branch of the predicate below never references it. Do not attempt to compensate for join-type mistakes with an `OR current_hold_id IS NULL` condition in `WHERE` — that does not fix row loss, it introduces row duplication instead (one spurious result row per unrelated `holds` row in the table), which corrupts the row-count check in step 4 below.
3. **Immediate Non-Blocking Contention Resolution:** Use `SELECT ... FOR UPDATE OF seats NOWAIT` inside the transaction, explicitly scoping the lock to the `seats` table only. A bare `FOR UPDATE NOWAIT` is invalid here and will be rejected by PostgreSQL, since `FOR UPDATE` cannot apply to the nullable side of an outer join (`holds`, under the `LEFT JOIN` above). Scoping the lock to `seats` is also correct on its own terms — `holds` is only being read here to check expiry, not modified, so it should not be locked, and doing so would create unnecessary contention with the sweeper (4.3), which writes to `holds` independently.
   * If a concurrent transaction is actively holding a physical lock on any of the target seat rows, PostgreSQL raises error code `55P03` (`lock_not_available`).
   * The backend catches this exception and aborts immediately with an HTTP `409 Conflict` ("Seat currently being processed").
4. **Availability Predicate:** The locking query's `WHERE` clause must explicitly evaluate:
   `seats.status = 'AVAILABLE' OR (seats.status = 'LOCKED' AND holds.expires_at < NOW())`
   * If the number of rows acquired and locked does **not** exactly match the number of requested seats, the transaction must execute an **all-or-nothing rollback** and return HTTP `409 Conflict`. This predicate is authoritative — application code does not re-check seat status or expiry after the query returns; it only performs the count check and, on success, proceeds to hold creation.
5. **Hold Generation:** An explicit `holds` record is created with a unique UUID (`hold_id`). The locked seats are updated with `status = 'LOCKED'` and `current_hold_id = hold_id` within the same transaction.

### 4.3. Expiration & Release Mechanics
* **Lazy Expiration on Read:** Seat map queries (`GET /events/{id}/seats`) compute display state dynamically. If a seat has `status = 'LOCKED'` but its associated hold's `expires_at < NOW()`, the query computes and returns its status as `AVAILABLE` without running write operations. The frontend polls this endpoint on a 4-second interval while viewing a seat map, so other users' holds and releases are reflected without requiring WebSockets/SSE.
* **Lazy Overwrite on Lock:** If an expired locked seat is targeted by a new user, the lock acquisition query safely locks and reassigns the seat to the new `hold_id`.
* **Asynchronous Sweeper (Decoupled Worker):** A lightweight background task running on a 15–30 second interval joins `seats` to `holds` to find seats with `status = 'LOCKED'` whose associated hold has `expires_at < NOW()` (using `SKIP LOCKED` where appropriate). On match, within a single transaction, it sets `seats.status = 'AVAILABLE'`, `seats.current_hold_id = NULL`, and `holds.status = 'EXPIRED'`. This cleans up state independently of frontend traffic. These three mechanisms (lazy-read, lazy-overwrite, sweeper) are intentionally redundant to guarantee correctness even in the total absence of read traffic on a given seat.
* **Explicit User Release:** If a user backs out or cancels, the backend releases the hold if and only if the request supplies the matching `hold_id` **and** the authenticated user (from the JWT) matches `holds.user_id`.
* **`current_hold_id` nulling rule:** `seats.current_hold_id` is nulled **only** by the expiry sweeper, to permit re-acquisition by a new hold. A successful checkout (4.4) never nulls it — `SOLD` is a terminal state in this MVP (no cancellation/refund-to-available flow exists), so a sold seat is never re-locked and its `current_hold_id` remains a permanent, valid pointer to the hold that produced it.

### 4.4. Late Checkout & Double-Selling Prevention
* Checkout runs a no-op/always-succeeds mock payment stub, then converts the hold into confirmed tickets and an order.
* **Hold-Validity Check at Checkout:** The checkout transaction must update the target seats to `status = 'SOLD'` conditional on `current_hold_id = :provided_hold_id` and `holds.status = 'ACTIVE'` and `holds.expires_at >= NOW()`. On success, in the same transaction, set `holds.status = 'COMPLETED'` and `holds.order_id = :new_order_id`.
* If zero rows are updated (e.g., the user paid after the 5-minute window and the seat was reassigned), the transaction rolls back, marks the hold as expired, rejects the purchase with an HTTP `409 Conflict`, and triggers the mock refund stub for the mock payment taken above.
* **Order Traceability:** `holds.order_id` is the sole link between a hold and the order it produced (nullable; set exactly once, in the same transaction as the `SOLD` update). Lookups from an order back to its hold use a reverse query (`WHERE holds.order_id = :order_id`) — `orders` itself carries no `hold_id` column. This is distinct from `holds.status = 'COMPLETED'`: status reflects lifecycle state, `order_id` reflects the specific order produced.

---

## 5. The AI Assistant Module (Strict Architectural Boundary)

* **Isolated Role:** The LLM engine acts strictly as a natural language semantic parser. It has zero database connectivity and never determines seat availability, pricing reality, or reservation state.
* **Flow:**
  1. Frontend submits query (e.g., *"Find 2 cheap seats near the stage"*) to Backend API.
  2. Backend forwards text to the separate LLM Engine microservice.
  3. LLM Engine queries the configured LLM provider with system instructions to return strict JSON validated against a Pydantic schema:
```json
     {
       "quantity": 2,
       "adjacency": true,
       "max_price": null,
       "preferred_section": "front"
     }
```
  4. Backend matches validated preferences against current, real-time `AVAILABLE` seats in PostgreSQL and returns candidate seat IDs to the user.

### 5.x POC Venue Grid & Seat Numbering
* **Layout:** 3 rows (`A`, `B`, `C`), 10 seats each.
* **`seat_number` is row-relative, not globally continuous.** Each row independently numbers its seats `1` through `10` (row B does not continue at 11, row C does not continue at 21). Seat identity/uniqueness is never derived from `seat_number` alone — every seat has a globally unique primary key `id`, which is what `current_hold_id` and all locking/hold logic reference. `row` + `seat_number` together are for display and adjacency purposes only.
* **Row = section/tier for this POC.** `seats.section` is derived from (or set equal to) `seats.row` — row `A` = front/premium, `B` = middle, `C` = top/back — each row carrying one price point. This satisfies the "seed data across tiers" deliverable (section 7) without introducing a separate section axis. A finer-grained section model (multiple sections within a row, non-uniform layouts) is out of scope for the POC and belongs on the roadmap.
* **`preferred_section` mapping:** the LLM's returned `preferred_section` value maps to a row as follows — `"front"` → `A`, `"middle"` → `B`, `"top"`/`"back"` → `C`.

### 5.y Candidate Seat Query Ordering
* Any query used to select candidate seats for the AI search feature must use an explicit `ORDER BY row ASC, seat_number ASC`. PostgreSQL does not guarantee row order without an explicit `ORDER BY`, even for repeated runs of the same query — so this ordering is required for "ascending" selection to be a guaranteed behavior, not an accidental one.

### 5.z Adjacency & Matching Algorithm
* **Contiguity definition:** two or more seats are adjacent only if they share the same `row` **and** their `seat_number` values form a consecutive run with no gaps, within that row. Seats in different rows are never considered adjacent, regardless of their `seat_number` values (e.g., row A's seat 10 and row B's seat 1 are not adjacent).
* **`adjacency: true`:** search for a contiguous block of exactly `quantity` seats (per the definition above), respecting `max_price`/`preferred_section` filters. If found, return it. If no such contiguous block exists, return an empty result — do not split the request across rows and do not fall back to non-contiguous seats. The user then falls back to manual seat selection.
* **`adjacency: false` or unset:** attempt the same contiguous-block search as a soft preference; if a match is found, return it. If not, fall back to returning the first `quantity` seats satisfying the other filters, using the `ORDER BY row ASC, seat_number ASC` ordering from 5.y. No restriction to a single section/row is required for this fallback.
* **No positional sub-preference** (e.g., corner seat, center seat, aisle seat) is supported or inferred, since the validated JSON schema (`quantity`, `adjacency`, `max_price`, `preferred_section`) has no field to express it. This is intentionally out of scope, not an oversight.

### 5.w Fault Tolerance
Two distinct empty-result cases must both be handled, and both resolved by falling back to manual seat selection — they must not be conflated with each other in logging, error handling, or the response returned to the frontend:
1. The LLM engine fails, times out, or returns invalid/unvalidatable JSON.
2. The LLM engine returns valid, successfully validated JSON, but the matching logic above (5.z) finds zero qualifying seats (e.g., no contiguous block of the requested size exists). This is a valid empty result, not an error state.

Core ticketing and manual seat selection must remain 100% operational regardless of which case occurs.

---

## 6. Verification & Automated Concurrency Testing

* In place of heavy external load frameworks, the repository must include an automated concurrency test script (using `pytest` + `asyncio.gather` / `httpx`).
* **The Collision Scenario:** 10+ asynchronous requests simultaneously target the exact same available seat ID at the same millisecond.
* **Pass Assertion:** Exactly 1 request completes with HTTP `200 OK` (hold acquired), while all other $N - 1$ requests return HTTP `409 Conflict`. Zero double-holds; database state remains consistent.

---

## 7. Deliverables Matrix
* **Frontend:** React / Next.js web application (login, event browsing, seat grid visualization, 5-minute hold timer, checkout flow, orders view, AI search input).
* **Backend:** FastAPI application exposing modular routes for authentication, seat maps, hold lifecycle, checkout, and order history. Authentication uses JWT (bearer token); the authenticated user's identity is always derived from the verified JWT, never from a client-supplied `user_id` field. Bearer-token compromise is an accepted MVP-level risk, to be mitigated later via the short-lived-access-token + HttpOnly-refresh-token upgrade noted in section 2's roadmap list.
* **LLM Engine:** Dedicated FastAPI service wrapping the configured LLM provider with strict Pydantic validation.
* **Database & Seed Data:** PostgreSQL migrations/schema script and a seed file creating an event with a multi-row seat map across tiers (see 5.x for the POC grid layout and row-as-tier mapping).
* **Testing & Documentation:** Automated Python concurrency verification test and a clean `README.md` detailing architecture, configuration, `.env.example`, and reproduction steps.