# User Flow Contracts Specification

**Feature Branch**: `006-frontend-user-flows`
**Date**: 2026-09-25

## 1. Page User Flows & API Mappings

| User Flow | Route Path | Trigger Action | Method & Endpoint | Payload / Params | Expected Response |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Registration** | `/register` | Form Submit | `POST /api/v1/auth/register` | `{email, password}` | `TokenResponse` (`access_token`) |
| **Login** | `/login` | Form Submit | `POST /api/v1/auth/login` | `{email, password}` | `TokenResponse` (`access_token`) |
| **Catalog** | `/events` | Page Load | `GET /api/v1/events` | None | `List[EventResponse]` |
| **Seat Map** | `/events/[id]` | Page Load & 4s Poll | `GET /api/v1/events/{id}/seats` | None | `SeatMapResponse` |
| **AI Search** | `/events/[id]` | Search Submit | `POST /api/v1/events/{id}/ai-search` | `{query}` | `AISearchResponse` |
| **Hold Lease** | `/events/[id]` | Click Hold | `POST /api/v1/events/{id}/holds` | `{seat_ids}` | `HoldResponse` |
| **Checkout** | `/events/[id]` | Click Checkout | `POST /api/v1/checkout/holds/{holdId}` | `{payment_token}` | `OrderResponse` |
| **My Orders** | `/orders` | Page Load | `GET /api/v1/orders` | None | `List[OrderResponse]` |
