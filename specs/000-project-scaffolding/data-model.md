# Data Model & Configuration Schemas: Project Scaffolding & Tooling

**Feature Branch**: `000-project-scaffolding` | **Date**: 2026-09-25

## Environment Configuration Entities

For Spec 0, the data model represents the environment configuration schemas and microservice environment contracts required to operate the application services.

### 1. Backend Service Configuration (`backend/.env.example`)

| Variable Name | Type | Default / Example Value | Description |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | String | `postgresql+asyncpg://postgres:postgres@localhost:5432/frontrow` | Async PostgreSQL database connection string |
| `JWT_SECRET` | String | `change-this-super-secret-key-in-production` | Secret key for JWT token signing & verification |
| `JWT_ALGORITHM` | String | `HS256` | JWT signature algorithm |
| `HOLD_DURATION_SECONDS` | Integer | `300` | Lease expiry duration for seat holds (5 minutes) |
| `LLM_ENGINE_URL` | String | `http://localhost:8001` | Base URL for LLM Engine microservice communication |

### 2. LLM Engine Configuration (`llm-engine/.env.example`)

| Variable Name | Type | Default / Example Value | Description |
| :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | String | `your_gemini_api_key_here` | API key for Google Gemini / LLM provider |
| `LLM_PROVIDER` | String | `gemini` | LLM provider selection (`gemini`, `openai`, etc.) |
| `PORT` | Integer | `8001` | LLM Engine HTTP service port |

### 3. Frontend Configuration (`frontend/.env.example`)

| Variable Name | Type | Default / Example Value | Description |
| :--- | :--- | :--- | :--- |
| `NEXT_PUBLIC_API_BASE_URL` | String | `http://localhost:8000` | Public API URL for backend HTTP calls |

---

## Service Directory Structure Model

```text
frontrow/
├── frontend/
│   ├── package.json          # Node.js app dependencies & scripts
│   ├── next.config.js        # Next.js configuration
│   └── .env.example          # Frontend environment template
├── backend/
│   ├── pyproject.toml        # Backend Python dependencies managed by uv
│   ├── alembic.ini           # Alembic database migration config
│   ├── alembic/              # Alembic revisions & env.py
│   └── .env.example          # Backend environment template
├── llm-engine/
│   ├── pyproject.toml        # LLM microservice dependencies managed by uv
│   └── .env.example          # LLM engine environment template
└── scripts/
    └── run_migrations.py     # Cross-platform migration runner script
```
