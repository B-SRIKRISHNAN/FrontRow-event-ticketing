<!--
SYNC IMPACT REPORT & REVISION HISTORY
======================================
NOTE: This cumulative changelog is a ONE-OFF RETROFITTING EXCEPTION because previous initial revisions (v1.0.0 through v1.2.0) were not individually committed to version control. Going forward, every constitution modification MUST be committed to git immediately upon change, and future header reports will document only their own single-version delta.

Current Version: 1.2.1

CUMULATIVE VERSION CHANGELOG:
-----------------------------
v1.2.1 (2026-09-25) [PATCH]
- Principle I: Refined Atomic Checkout to mandate mock payment stub execution and atomic updating of holds.status = 'COMPLETED' and holds.order_id = :new_order_id on successful checkout.

v1.2.0 (2026-09-25) [MINOR]
- Principle VIII: Added strict Alembic migration rule (backend/alembic/), local migration runner script requirement, and DML-only seeding scripts.

v1.1.0 (2026-09-25) [MINOR]
- Principle VI: Added mandatory Pydantic schema validation across all API endpoints, DTOs, and inter-service LLM outputs.
- Principle VII: Added zero secret leakage rule (.env.example exclusivity, gitignore enforcement, no committed credentials).

v1.0.0 (2026-09-25) [MAJOR]
- Initial ratification from blueprint.md. Established Principles I–V (concurrency & DB locking, 4-part architectural separation, tri-layer lease lifecycle, AI candidate matching, automated concurrency verification) and core domain entities.

DEPENDENT TEMPLATES ALIGNMENT:
- .specify/templates/plan-template.md: ✅ Aligned
- .specify/templates/spec-template.md: ✅ Aligned
- .specify/templates/tasks-template.md: ✅ Aligned
-->

# FrontRow Constitution

## Core Principles

### I. Absolute Concurrency & Double-Selling Immunity (NON-NEGOTIABLE)
The system MUST guarantee zero double-selling and absolute state consistency under high concurrency.
- **Physical DB Lock Duration**: Physical database locks MUST be ultra-short (~2ms to 5ms) and bounded strictly inside an explicit database transaction block. Never keep a physical database lock or connection open while awaiting user input or external calls.
- **Deterministic Acquisition**: Seat IDs in multi-seat hold requests MUST be ordered ascending (`ORDER BY id ASC`) to prevent circular transaction deadlocks.
- **Join Construction**: Seat locking queries MUST use a `LEFT JOIN` from `seats` to `holds` on `current_hold_id`. `INNER JOIN` or comma-joins with equality in `WHERE` are explicitly forbidden because they silently drop unheld `AVAILABLE` seats.
- **Immediate Non-Blocking Contention Resolution**: Seat locking queries MUST use `SELECT ... FOR UPDATE OF seats NOWAIT`. Locking MUST be explicitly scoped to `seats` to avoid locking the `holds` table. Catch PostgreSQL error code `55P03` (`lock_not_available`) and abort immediately with HTTP `409 Conflict`.
- **Atomic Availability Predicate**: The locking query's `WHERE` clause MUST explicitly evaluate `seats.status = 'AVAILABLE' OR (seats.status = 'LOCKED' AND holds.expires_at < NOW())`. If the count of locked rows does not exactly match requested seats, execute an all-or-nothing transaction rollback and return HTTP `409 Conflict`.
- **Atomic Checkout**: Checkout MUST first execute a no-op/always-succeeds mock payment stub. The checkout transaction MUST then update the target seats to `status = 'SOLD'` conditional on `current_hold_id = :provided_hold_id`, `holds.status = 'ACTIVE'`, and `holds.expires_at >= NOW()`. On success, within the same transaction, set `holds.status = 'COMPLETED'` and `holds.order_id = :new_order_id`. If zero rows are updated (e.g., the hold expired or was reassigned before payment completed), roll back, mark the hold as expired, reject with HTTP `409 Conflict`, and trigger the mock refund stub for the mock payment taken above.

### II. Clean Architectural Separation & Security Boundaries
The system MUST enforce strict decoupling across the four core layers: Frontend, Backend API, LLM Engine microservice, and PostgreSQL Database.
- **Communication Boundaries**: Frontend ↔ Backend API ↔ LLM Engine & PostgreSQL. The frontend MUST NEVER communicate directly with the LLM engine microservice or PostgreSQL database.
- **LLM Isolation**: The LLM engine microservice is strictly a read-only natural language semantic parser. It MUST NOT possess database connectivity, nor make seat availability, pricing, or reservation decisions.
- **Authentication & User Identity**: Backend API authentication MUST use JWT (bearer tokens). User identity for all hold, release, and order operations MUST be derived strictly from verified JWT claims, NEVER from client-supplied body or query parameters (`user_id`).

### III. Tri-Layer Lease Lifecycle Management
Logical seat holds MUST be strictly managed using a 5-minute checkout lease window (environment-configurable).
- **Single Source of Expiry Truth**: `expires_at` MUST live exclusively on the `holds` table (`holds.expires_at`). Seats MUST NOT carry their own expiry timestamp.
- **Redundant Expiry Enforcement**: Hold expirations MUST be enforced across three redundant mechanisms:
  1. *Lazy Expiration on Read*: `GET /events/{id}/seats` dynamically calculates and displays expired locked seats as `AVAILABLE` without write database operations.
  2. *Lazy Overwrite on Lock*: Lock acquisition queries safely overwrite expired locked seats within the atomic locking transaction.
  3. *Asynchronous Sweeper Worker*: A background worker running on a 15–30s interval queries expired locked seats (`SKIP LOCKED`) and updates `seats.status = 'AVAILABLE'`, `seats.current_hold_id = NULL`, and `holds.status = 'EXPIRED'` in a single transaction.
- **Hold Reference Nulling**: `seats.current_hold_id` MUST ONLY be nulled by the asynchronous sweeper worker upon lease expiration. Successful checkouts MUST NOT null `current_hold_id`, leaving it as a permanent pointer to the creating hold.

### IV. Deterministic Candidate Seat Matching & AI Parsing Boundary
Natural language AI seat search MUST operate within strict semantic boundaries and deterministic seat matching algorithms.
- **Pydantic Validation**: The LLM microservice MUST return strict JSON validated against a Pydantic schema containing `quantity` (int), `adjacency` (bool), `max_price` (float/null), and `preferred_section` (str/null).
- **Candidate Query Ordering**: Candidate seat selection queries MUST explicitly specify `ORDER BY row ASC, seat_number ASC`.
- **Contiguity Definition**: Seat adjacency is defined strictly as consecutive `seat_number` values within the exact same `row`. Seats across different rows are never contiguous.
- **Adjacency Matching Rules**: If `adjacency` is true, the system MUST return a single contiguous block of `quantity` seats within one row or return an empty result. If `adjacency` is false/unset, contiguous blocks are preferred, falling back to non-contiguous matching ordered by `row ASC, seat_number ASC`.
- **Fault Tolerance**: LLM service failures (timeouts, invalid JSON) and valid empty seat search matches MUST both gracefully fall back to manual seat selection without crashing or conflating failure modes in logs.

### V. Empirical Automated Concurrency Verification
All concurrency and state integrity assertions MUST be proven through automated testing.
- **Mandatory Concurrency Suite**: The repository MUST maintain automated Python concurrency tests using `pytest` + `asyncio.gather` / `httpx`.
- **Collision Test Assertion**: Under simultaneous collision where 10+ concurrent requests target the exact same available seat at the same millisecond, exactly 1 request MUST succeed with HTTP `200 OK` (hold acquired), while all $N - 1$ remaining requests MUST return HTTP `409 Conflict`. Zero double-holds or corrupted states are permitted.

### VI. Mandatory Pydantic Schema & Type Safety Discipline
All data structures, request payloads, response DTOs, and inter-service communications MUST be strongly typed using Pydantic models.
- **API Request/Response Validation**: All FastAPI endpoints across backend and LLM engine services MUST define and enforce explicit Pydantic schemas for input validation and output serialization. Unvalidated dictionaries or untyped JSON payloads are strictly prohibited.
- **LLM Structured Output Parsing**: Inter-service messages from the LLM Engine microservice MUST be parsed and validated against strict Pydantic schemas before being processed by Backend API matching logic.

### VII. Zero Secret Leakage & Environment Hygiene (NON-NEGOTIABLE)
No secret, credential, API key, certificate, or private environment file (`.env`, `.env.local`, `.pem`, `.key`, etc.) shall EVER be committed to version control, included in spec-kit artifacts, or exposed in logs.
- **`.env.example` Exclusivity**: Version control MUST strictly contain `.env.example` template files only. These files MUST list required variable names with safe placeholder values or explanatory comments (e.g. `DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/frontrow`), but MUST NEVER contain real credentials, production connection strings, or secret keys.
- **Git Ignore Enforcement**: All active `.env` files, private credential files, and local developer overrides MUST be ignored in `.gitignore`.

### VIII. Strict Alembic Database Schema Migrations
All database schema definitions, table modifications, column types, and index creations MUST be managed exclusively via Alembic migrations (`backend/alembic/`).
- **Exclusive Migration Authority**: Creating, altering, or dropping database tables or columns via raw SQL queries, `Base.metadata.create_all()`, or ad-hoc scripts outside of Alembic migration scripts is strictly prohibited.
- **Local Migration Runner Script**: The project MUST provide a dedicated migration runner script (e.g. `scripts/run_migrations.py` or shell equivalent) to execute Alembic migrations cleanly during local development setup, testing, and deployment workflows.
- **DML-Only Seed Data**: Data seeding scripts (`scripts/seed_event.py`) MUST assume schema migration completion and execute DML statements (`INSERT` / `UPDATE`) only, never DDL schema changes.

## Technology Stack & Operational Boundaries

- **Frontend**: React / Next.js web application.
- **Backend API**: Python FastAPI utilizing SQLAlchemy / ORM with `asyncpg` for PostgreSQL connection management, with Pydantic for request/response validation. Database migrations managed exclusively via Alembic (`backend/alembic/`).
- **LLM Engine**: Python FastAPI microservice wrapping an abstracted LLM provider interface (default Gemini; provider swappable via env config), using Pydantic for strict output schema validation.
- **Primary Database**: PostgreSQL with explicit ACID transaction boundaries and row-level locking (`SELECT ... FOR UPDATE OF seats NOWAIT`). All schema changes applied via Alembic migrations run via local migration runner script.
- **Environment Configuration**: All service configuration, credentials, API keys, and logical hold durations MUST be loaded via `.env` files. Each standalone service (`frontend/`, `backend/`, `llm-engine/`) MUST contain its own independent `.env.example` file. Real secrets, keys, and `.env` files MUST NEVER be committed.
- **MVP Exclusions**: Redis distributed locks, WebSockets/SSE streaming, Locust load testing, refresh tokens / cookie session upgrades, and multi-section row venue models are explicitly out of scope for MVP and documented for future roadmap iteration.

## Core Domain Entities & Relational Integrity Rules

- **Users (`users`)**: Authentication and order ownership.
- **Events (`events`)**: Event metadata, venue layout, and timing.
- **Seats (`seats`)**: Individual physical seats containing `row`, `seat_number`, `section` (derived from/equal to `row`), `price`, operational `status` (`AVAILABLE`, `LOCKED`, `SOLD`), and nullable `current_hold_id`. `seat_number` resets per row; primary key `id` provides global uniqueness.
- **Holds (`holds`)**: Reservation lease tracking `user_id`, `event_id`, `status` (`ACTIVE`, `COMPLETED`, `EXPIRED`), creation timestamp, `expires_at` (5 min default), and nullable `order_id`. Holds associate with one or many seats.
- **Orders & Tickets (`orders`, `tickets`)**: Confirmed transactions post-checkout. `holds.order_id` is the sole link between a hold and its produced order; reverse lookup `WHERE holds.order_id = :order_id` is used (`orders` carries no `hold_id` column).

## Governance

1. **Supremacy**: This Constitution supersedes all other documentation, architectural designs, and implementation decisions within the FrontRow project.
2. **Amendment Process**: Amendments require formal documentation, explicit review of concurrency impact, update of all dependent templates (`plan-template.md`, `spec-template.md`, `tasks-template.md`), a version bump, and MUST be committed immediately to version control upon ratification. Going forward, each commit MUST contain only its own single-version header report.
3. **Versioning Policy**:
   - **MAJOR**: Backward incompatible governance, principle removals, or redefinitions of locking/separation boundaries.
   - **MINOR**: Addition of new principles, domain entity rules, or expanded architectural guidance.
   - **PATCH**: Wording clarifications, typo fixes, or non-semantic refinements.
4. **Compliance Review**: All Pull Requests and feature specifications MUST be verified against these principles. Violations MUST be rejected or formally justified in the plan's Complexity Tracking matrix.

**Version**: 1.2.1 | **Ratified**: 2026-09-25 | **Last Amended**: 2026-09-25
