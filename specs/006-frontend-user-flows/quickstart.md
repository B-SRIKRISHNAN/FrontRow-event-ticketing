# Quickstart & Validation Guide: Frontend User Flows

**Feature Branch**: `006-frontend-user-flows`
**Date**: 2026-09-25

This guide provides step-by-step instructions to validate the complete end-to-end ticketing flow from account registration to real-time seat holds and confirmed orders.

---

## Prerequisites

1. **Backend API Server**: Ensure FastAPI backend is running on `http://localhost:8000`:
   ```powershell
   cd d:\projects\interviews\FrontRow-event-ticketing\backend
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --reload
   ```
2. **LLM Engine Microservice**: Ensure LLM microservice is running on `http://localhost:8001`:
   ```powershell
   cd d:\projects\interviews\FrontRow-event-ticketing\llm-engine
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --reload
   ```
3. **Frontend Server**: Launch Next.js dev server on `http://localhost:3000`:
   ```powershell
   cd d:\projects\interviews\FrontRow-event-ticketing\frontend
   npm run dev
   ```

---

## Complete End-to-End Validation Scenario

1. **Register User Account**:
   - Open `http://localhost:3000/register` in your browser.
   - Enter email `buyer@frontrow.com` and password `password123`.
   - Click **Register Account**.
   - **Verification**: User is redirected to `/events`, Navbar header displays `buyer@frontrow.com`.

2. **Browse Events & Open Seat Map**:
   - On `/events`, click **View Seat Map & Reserve** for "FrontRow World Championship 2026".
   - **Verification**: Navigates to `/events/1`. Seat grid renders with green `AVAILABLE` seat cells.

3. **AI Seat Search**:
   - In the AI Search box at top of seat map, type `2 seats together under $150`.
   - Click **Search with AI**.
   - **Verification**: LLM microservice parses query; candidate seats (e.g. Seats 1 & 2) are automatically highlighted in cyan `SELECTED` state.

4. **Acquire 5-Minute Seat Hold Lease**:
   - With Seats 1 & 2 selected, click **Hold 2 Selected Seats**.
   - **Verification**: Active `CountdownTimer` appears displaying `04:59` lease countdown. Held seats transition to `SELECTED` hold state. "Proceed to Checkout" panel appears.

5. **Complete Checkout & View Ticket Receipt**:
   - Click **Complete Checkout ($300.00)**.
   - **Verification**: Toast success banner appears ("Checkout Successful! Seats converted to SOLD."). User is redirected to `/orders`.

6. **Verify Order History**:
   - On `/orders`, inspect the new purchase card.
   - **Verification**: Order ID, total amount ($300.00), and ticket badges (Row A Seat 1, Row A Seat 2) render cleanly.
