# Quickstart & Validation Guide: Project Scaffolding & Tooling

**Feature Branch**: `000-project-scaffolding` | **Date**: 2026-09-25

## Setup & Verification Steps

Follow these steps to verify that the project scaffolding, independent service environments, `.env.example` templates, and migration runner script are configured correctly.

### Prerequisites

- Python 3.11+
- `uv` installed (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Node.js 18+ and `npm`

---

### Step 1: Verify Directory Layout & `.env.example` Templates

Verify that all required service directories exist and contain independent `.env.example` templates enforcing Constitution Principle VII:

```bash
# Check top-level directories
ls -d frontend backend llm-engine scripts

# Verify .env.example files exist
ls -l frontend/.env.example backend/.env.example llm-engine/.env.example
```

---

### Step 2: Initialize Backend Virtual Environment & Dependencies

Initialize the isolated virtual environment for `backend/` using `uv`:

```bash
cd backend
uv sync
```

Verify that `pyproject.toml` and `uv.lock` are generated inside `backend/` without affecting other services.

---

### Step 3: Initialize LLM Engine Virtual Environment & Dependencies

Initialize the isolated virtual environment for `llm-engine/` using `uv`:

```bash
cd ../llm-engine
uv sync
```

Verify that `pyproject.toml` and `uv.lock` are generated inside `llm-engine/` independently.

---

### Step 4: Initialize Frontend Dependencies

Initialize the Next.js JavaScript application in `frontend/`:

```bash
cd ../frontend
npm install
```

---

### Step 5: Test Cross-Platform Migration Runner Script

From the repository root, invoke the migration runner script:

```bash
# Create local .env from .env.example inside backend/
cp backend/.env.example backend/.env

# Run migration script
python scripts/run_migrations.py
```

Expected Outcome: The script reads the database configuration, verifies connection settings, and invokes Alembic migration upgrade commands cleanly.
