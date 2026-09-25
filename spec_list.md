# FrontRow — Development Spec Roadmap

## Spec 0 — Project Scaffolding & Tooling
- Repo structure per constitution section 8 (`frontend/`, `backend/`, `llm-engine/`, `scripts/`, root `docker-compose.yml` optional).
- `uv`-managed Python projects for `backend/` and `llm-engine/` (separate `pyproject.toml`/lockfile each — independent services, not a shared monorepo Python env).
- Next.js app initialized in `frontend/` (App Router; confirm TypeScript or JS).
- Alembic initialized under `backend/alembic/`, wired to the SQLAlchemy/asyncpg setup.
- Per-service `.env.example` files (Principle VII) — no real `.env` committed.
- Placeholder migration-runner script (`scripts/run_migrations.py` or shell equivalent, Principle VIII) — can be a stub until schema exists.

---

## Spec 1 — Database Schema & Migrations
- Table-by-table design: `users`, `events`, `seats`, `holds`, `orders`, `tickets` — types, constraints, indexes (especially `seats.current_hold_id`, `holds.expires_at`, `holds.order_id`).
- Alembic migration authoring for all tables (Principle VIII: exclusive migration authority, no raw DDL).
- Seed script (`scripts/seed_event.py`) — DML-only, POC 3×10 A/B/C grid per constitution section 5.x.

---

## Spec 2 — Core Backend API (Ticketing)

Grouped as one spec across shared-schema flows to avoid cross-spec drift:

- Auth: register/login, JWT issuance, identity-from-claims enforcement (Principle II).
- **DB engine & connection pooling setup:** SQLAlchemy async engine with explicit connection pool (not single/shared connection) — pool sized to exceed the collision test's concurrency level (≥15 recommended: `pool_size`, `max_overflow`, `pool_timeout`, `pool_pre_ping`); separate small pool/connection for the sweeper worker, isolated from the request-serving pool.
- Events & seat map: `GET /events`, `GET /events/{id}/seats` (lazy-expiry read logic, 4s-poll-compatible).
- Hold acquisition: `POST /events/{id}/holds` (full Principle I logic — `LEFT JOIN`, `FOR UPDATE OF seats NOWAIT`, availability predicate, count-check rollback). Concurrency-critical queries (hold acquisition, sweeper, checkout) written as raw parameterized SQL via SQLAlchemy's `text()`/execute path, not the ORM query builder; all other queries use standard ORM patterns.
- Explicit release: `DELETE /holds/{hold_id}` (ownership check against JWT).
- Checkout: `POST /holds/{hold_id}/checkout` (mock payment stub → conditional `SOLD` update → `COMPLETED`/`order_id` write → mock refund on failure).
- Orders: `GET /orders`.
- AI-search endpoint's shape and fallback contract built here too, calling a stubbed/fake LLM response for now — real LLM integration deferred to Spec 4.
- Asynchronous sweeper worker (Principle III, mechanism 3).
- **Checkpoint:** OpenAPI/Swagger contract reviewed against constitution principles before frontend work begins.

---

## Spec 3 — Backend Test Suite

Two explicitly separate tracks:

- **Unit tests** (service/controller layers, mocked DB): validation, auth/JWT checks, adjacency-matching logic, fault-tolerance branches, error responses.
- **Integration/concurrency tests** (real Postgres, ephemeral test DB, migrations applied): Principle V's collision scenario, atomic hold acquisition, atomic checkout — must run against a genuine DB; no mocking permitted here.
  - **Dedicated, standalone concurrency proof test:** `backend/tests/test_concurrency.py`, individually runnable (`pytest tests/test_concurrency.py -v`), separate from the general suite invocation, per the brief's "strongly encouraged" demonstration requirement.
  - Must produce **extensive, step-by-step console logging**, not just a pass/fail assertion — e.g.: setup (seed state confirmed, target seat ID + initial status logged), dispatch (each of the 10+ concurrent requests logged as fired, with a timestamp/index), per-request outcome as it resolves (which request got `200 OK` vs `409 Conflict`, and — where obtainable — whether it hit the `55P03` lock-contention path or the availability-predicate/count-mismatch path), and a final summary block (e.g., "9/10 correctly rejected, 1/10 succeeded, seat X now `LOCKED` with hold Y, zero double-holds detected").
  - This log output is the actual reviewer-facing proof artifact — the test must remain readable and unambiguous even before anyone reads the assertion code itself.
  - Note in the test file that the connection pool sizing from Spec 2 is itself a precondition for test validity (a too-small pool would bottleneck at the app layer before ever reaching Postgres's lock manager) — don't let it be "optimized" down without understanding why it's sized that way.

---

## Spec 4 — LLM Engine Microservice
- Swappable provider interface, default Gemini (Principle II isolation, Principle VI Pydantic output schema).
- Prompt design for `{quantity, adjacency, max_price, preferred_section}`.
- Swap backend's Spec 2 stub for a real call to this service; timeout/failure handling exercised end-to-end.
- Adjacency/contiguity matching logic finalized against constitution section 5.x/5.z rules (row-as-tier, per-row seat numbering, no cross-row splits).

---

## Spec 5 — Frontend Skeleton & Dependencies
- Next.js project structure, routing, base layout, API client setup (base URL from env, JWT storage/attachment).
- Shared components scaffold (seat grid cell, countdown timer, toast/error display) — no full flow logic yet.

---

## Spec 6 — Frontend User Flows

Each flow as an acceptance-scenario section within this one spec:

- Register / login.
- Browse events → seat map view (available/held/sold, 4s polling).
- Select seats → hold → countdown timer → checkout.
- Orders/tickets view.
- AI search input → candidate seats → manual fallback path.

### Demo 1 Checkpoint
Full stack running via the init script; if seamless, proceed to enhancements from the constitution's roadmap list (Redis, WebSockets/SSE, refresh-token/cookie auth, finer venue modeling); if not, fix and re-checkpoint before touching enhancements.

---

## Spec 7 — Init Script & README Finalization
- One-shot script: create real `.env` files from examples (or prompt for values), run Alembic migrations via the runner script, run seed script, start all three services.
- README: architecture summary, setup steps, `.env.example` walkthrough, how to run tests (both tracks, noting the concurrency test's standalone invocation and its log-based proof output), reproduction steps for the concurrency test specifically.
- Also include a brief note on how our concurrency logic is valid and prevents two people booking the same seat(s):

### Concurrency Correctness — Design Note

**The guarantee:** if two or more buyers attempt to hold or buy the same seat(s) at the exact same instant, exactly one succeeds and all others receive an immediate, clear rejection — never a double-hold, never a double-sell.

**Why this holds, step by step:**

1. **The seat row itself is the single source of truth for availability**, guarded by PostgreSQL's own row-level locking — not application logic, not a distributed lock, not optimistic retry. Every hold attempt runs `SELECT ... FOR UPDATE OF seats NOWAIT` inside an explicit transaction. This asks Postgres itself to grant an exclusive physical lock on the target seat row before anything else happens.

2. **Only one transaction can hold that physical lock at a time.** If two requests arrive at the same seat simultaneously, Postgres's lock manager — not our code — deterministically admits one and makes the other fail immediately. Because we use `NOWAIT`, the losing request doesn't queue or block; it gets an instant `55P03` (`lock_not_available`) error, which we catch and turn into a `409 Conflict`. This is the actual mechanism that prevents the race — it's enforced by the database engine's own concurrency control, which is designed exactly for this class of problem.

3. **Winning the physical lock isn't enough on its own — the availability predicate is checked inside that same locked transaction.** Once a request has the row lock, it evaluates `status = 'AVAILABLE' OR (status = 'LOCKED' AND expires_at < NOW())`. If the seat was already taken (by a hold that hasn't expired), the predicate excludes it, so it's absent from the result set. We then compare the count of seats returned against the count requested — any mismatch triggers an **all-or-nothing rollback**, so a multi-seat request can never partially succeed and leave the buyer holding some but not all of what they asked for.

4. **The transaction is short.** The physical lock is only ever held for the few milliseconds it takes to check availability and write the new `HELD`/hold record — never while waiting on user input or payment. This means the lock isn't a bottleneck; it exists only long enough to make the availability decision atomic.

5. **Expiry is enforced redundantly, so a stale hold can never block a seat forever:** a lazy check on every read recalculates true status on the fly, a lazy overwrite lets a new hold safely reclaim an expired seat at acquisition time, and a background sweeper independently cleans up expired holds even with no read traffic at all. All three converge on the same rule — an expired hold has zero claim on the seat — so there's no path by which an abandoned hold can outlive its 5-minute window and block another buyer.

6. **Checkout uses the identical pattern as a final safeguard.** Converting a hold into a sale updates the seat to `SOLD` only if it's still tied to the *exact* hold presented, that hold is still `ACTIVE`, and it hasn't expired — all three checked atomically in one conditional update. If the buyer waited too long and the seat was reassigned in the meantime, zero rows are affected, the transaction rolls back, and the purchase is rejected — even at the very last step, there is no path to selling a seat that's no longer legitimately reserved by that buyer.

**How we convinced ourselves this is correct:** rather than relying on argument alone, the repository includes an automated test that fires 10+ simultaneous hold requests at the identical seat at the same moment and asserts exactly one returns `200 OK` while every other request returns `409 Conflict`, with zero double-holds in the resulting database state. The test logs each request's dispatch and outcome individually, so the result is directly observable, not just asserted.