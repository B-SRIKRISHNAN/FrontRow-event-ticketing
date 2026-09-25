# Quickstart & Validation Guide: Init Script & README Finalization

**Feature Branch**: `007-init-script-readme-finalization`
**Date**: 2026-09-25

This guide details the step-by-step instructions to validate the one-shot initialization script, verify `README.md`, and execute the automated concurrency proof test suite.

---

## 1. Validate One-Shot Initialization Script

1. **Run One-Shot Init Script**:
   ```powershell
   python init.py
   ```
   Or on Windows PowerShell:
   ```powershell
   .\init.ps1
   ```

2. **Verify Setup Steps**:
   - Check `.env` files are created in root, `backend/`, `llm-engine/`, and `frontend/`.
   - Verify Alembic migrations and `seed_event.py` execution.
   - Confirm services are running:
     - Backend API: `http://localhost:8000/health` -> `{"status": "ok"}`
     - LLM Engine: `http://localhost:8001/health` -> `{"status": "healthy"}`
     - Frontend: `http://localhost:3000` -> Landing page

---

## 2. Validate Concurrency Collision Proof Test

1. **Execute Concurrency Proof Test**:
   ```powershell
   python backend/tests/test_concurrency.py
   ```

2. **Verify Results**:
   - Assert exactly 1 request returns `200 OK` (hold acquired).
   - Assert all remaining 14 requests return `409 Conflict`.
   - Verify zero double-holds in PostgreSQL database.

---

## 3. Validate Test Suite Tracks

1. **Backend Unit & Integration Tests**:
   ```powershell
   cd backend
   pytest
   ```
2. **Frontend Production Build**:
   ```powershell
   cd frontend
   npm run build
   ```
