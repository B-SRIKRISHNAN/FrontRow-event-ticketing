# Quickstart & Validation Guide: LLM Engine Microservice

**Feature Branch**: `004-llm-engine-microservice`
**Date**: 2026-09-25

This guide provides runnable commands to launch the LLM Engine microservice, test query parsing in both mock and Gemini modes, and validate end-to-end backend integration with contiguity seat matching.

---

## Prerequisites

1. **Working Directory**: Open terminal in project root.
2. **Environment Configuration**: Ensure `llm-engine/.env` contains:
   ```env
   LLM_PROVIDER=mock
   PORT=8001
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
3. **Backend Configuration**: Ensure `backend/.env` contains:
   ```env
   LLM_ENGINE_URL=http://localhost:8001
   ```

---

## Scenario 1: Launch LLM Engine Microservice (Mock Mode)

Start the LLM Engine microservice standalone on port 8001:

```powershell
cd d:\projects\interviews\FrontRow-event-ticketing\llm-engine
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --reload
```

---

## Scenario 2: Validate LLM Parsing Endpoint directly

In a separate terminal, test the `POST /api/v1/parse-query` endpoint:

```powershell
curl -X POST "http://localhost:8001/api/v1/parse-query" `
  -H "Content-Type: application/json" `
  -d "{\"query\": \"Find me 2 seats together near Section A under $120\"}"
```

### Expected Output
```json
{
  "quantity": 2,
  "adjacency": true,
  "max_price": 120.0,
  "preferred_section": "A"
}
```

---

## Scenario 3: End-to-End Backend Search & Contiguity Validation

With both Backend API (:8000) and LLM Engine (:8001) running, trigger natural language seat search from Backend API:

```powershell
curl -X POST "http://localhost:8000/api/v1/events/1/ai-search" `
  -H "Content-Type: application/json" `
  -d "{\"query\": \"3 tickets together under $200\"}"
```

### Expected Outcome
- Backend receives query, calls LLM Engine (`POST http://localhost:8001/api/v1/parse-query`).
- LLM Engine returns `quantity: 3`, `adjacency: true`.
- Backend executes `SeatMatcher` contiguity logic on event 1 seats.
- Returns 3 candidate seat IDs in the exact same row with consecutive seat numbers.

---

## Scenario 4: LLM Timeout & Failure Fallback Validation

Stop the LLM Engine microservice process (simulate server down / timeout) and execute backend search:

```powershell
curl -X POST "http://localhost:8000/api/v1/events/1/ai-search" `
  -H "Content-Type: application/json" `
  -d "{\"query\": \"2 seats together\"}"
```

### Expected Outcome
- Backend logs a warning: `LLM service call failed or timed out. Falling back to manual seat selection.`
- Returns HTTP `200 OK` with:
  ```json
  {
    "quantity": 2,
    "adjacency": true,
    "max_price": null,
    "preferred_section": null,
    "recommended_seat_ids": [],
    "fallback_to_manual": true
  }
  ```
- **Zero HTTP 500 errors!**

---

## Scenario 5: Run Automated Microservice & Backend Test Suite

Execute Pytest suites for both services:

```powershell
# Run LLM Engine Unit Tests
cd d:\projects\interviews\FrontRow-event-ticketing\llm-engine
.\.venv\Scripts\python.exe -m pytest tests/ -v

# Run Backend Integration Tests
cd d:\projects\interviews\FrontRow-event-ticketing\backend
.\.venv\Scripts\python.exe -m pytest tests/test_sweeper.py -v
```
