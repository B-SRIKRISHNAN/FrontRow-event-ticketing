# Data Model: Init Script & README Finalization

**Feature Branch**: `007-init-script-readme-finalization`
**Date**: 2026-09-25

## Configuration & Environment Entities

### 1. Environment Variable Template (`.env.example`)

Represented across root and sub-service directories (`backend/.env.example`, `llm-engine/.env.example`, `frontend/.env.example`):

| Variable Name | Default / Example Value | Service Scope | Purpose |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/frontrow` | Backend | PostgreSQL connection string |
| `JWT_SECRET` | `super_secret_frontrow_jwt_key_change_in_prod_12345` | Backend | Secret key for JWT token signing |
| `HOLD_DURATION_SECONDS` | `300` | Backend | Logical seat hold lease duration (5 minutes) |
| `LLM_ENGINE_URL` | `http://localhost:8001` | Backend | Microservice URL for LLM query parser |
| `GEMINI_API_KEY` | `your_gemini_api_key_here` | LLM Engine | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-1.5-flash` | LLM Engine | Gemini model name |
| `LLM_PROVIDER` | `gemini` | LLM Engine | Active provider selection (`gemini` or `mock`) |
| `PORT` | `8001` | LLM Engine | HTTP listener port for LLM microservice |
| `NEXT_PUBLIC_API_BASE_URL`| `http://localhost:8000` | Frontend | Core Backend API endpoint URL |

---

### 2. Init Script Runner Config

| Field | Type | Description |
| :--- | :--- | :--- |
| `root_dir` | `Path` | Absolute path to repository root |
| `backend_dir` | `Path` | Absolute path to `backend/` directory |
| `llm_engine_dir` | `Path` | Absolute path to `llm-engine/` directory |
| `frontend_dir` | `Path` | Absolute path to `frontend/` directory |
| `services` | `List[Dict]` | Service runner definitions (`name`, `cwd`, `cmd`, `port`) |
