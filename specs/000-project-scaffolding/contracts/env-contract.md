# Interface Contract: Environment & Migration Runner Specifications

**Feature Branch**: `000-project-scaffolding` | **Date**: 2026-09-25

## 1. Environment Variable Specifications

### Backend Service (`backend/.env.example`)

```ini
# Database Connection String (SQLAlchemy asyncpg)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/frontrow

# JWT Authentication Configuration
JWT_SECRET=change-this-super-secret-key-in-production
JWT_ALGORITHM=HS256

# Logical Seat Lease Hold Window (in seconds, default 5 minutes)
HOLD_DURATION_SECONDS=300

# LLM Microservice Endpoint
LLM_ENGINE_URL=http://localhost:8001
```

### LLM Engine Microservice (`llm-engine/.env.example`)

```ini
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# LLM Provider Selection (gemini, openai)
LLM_PROVIDER=gemini

# HTTP Port
PORT=8001
```

### Frontend Application (`frontend/.env.example`)

```ini
# Backend API Base URL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## 2. Migration Runner Script CLI Contract (`scripts/run_migrations.py`)

### Invocation Syntax

```bash
python scripts/run_migrations.py [--revision REVISION] [--backend-dir BACKEND_DIR]
```

### Contract Rules

1. Must locate `backend/.env` (or environment variables) to resolve `DATABASE_URL`.
2. Must raise explicit error message if `DATABASE_URL` is missing or unconfigured.
3. Must invoke Alembic migration runner programmatically against `backend/alembic.ini`.
4. Must return exit code `0` on successful migration upgrade to `head`.
5. Must return exit code `1` with formatted error message on connection failure or migration error.
