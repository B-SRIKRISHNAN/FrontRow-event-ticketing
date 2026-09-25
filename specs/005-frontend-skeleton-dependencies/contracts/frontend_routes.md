# Frontend Route Contract Specification

**Feature Branch**: `005-frontend-skeleton-dependencies`
**Date**: 2026-09-25

## App Router Route Hierarchy

| Route Path | File Location | Public / Auth | Page Purpose | Backend API Mapping |
| :--- | :--- | :--- | :--- | :--- |
| `/` | `app/page.js` | Public | Landing page & brand introduction | N/A |
| `/login` | `app/login/page.js` | Public | User authentication form | `POST /api/v1/auth/login` |
| `/register` | `app/register/page.js` | Public | User registration form | `POST /api/v1/auth/register` |
| `/events` | `app/events/page.js` | Public | Event catalog listing | `GET /api/v1/events` |
| `/events/[id]` | `app/events/[id]/page.js` | Public / Auth | Interactive seat map & hold reservation | `GET /api/v1/events/{id}/seats`<br>`POST /api/v1/events/{id}/holds`<br>`POST /api/v1/events/{id}/ai-search` |
| `/orders` | `app/orders/page.js` | Authenticated | Order history & confirmed tickets view | `GET /api/v1/orders` |

---

## API Client Endpoint Call Contract (`lib/api.js`)

```javascript
import { api } from '@/lib/api';

// Example API calls using centralized client:
const events = await api.get('/api/v1/events');
const seats = await api.get(`/api/v1/events/${eventId}/seats`);
const hold = await api.post(`/api/v1/events/${eventId}/holds`, { seat_ids: [1, 2] });
const order = await api.post(`/api/v1/checkout/holds/${holdId}`, { payment_token: 'mock_token' });
```
