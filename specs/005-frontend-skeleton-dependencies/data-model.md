# Data Model & Schema Specification: Frontend Skeleton & Dependencies

**Feature Branch**: `005-frontend-skeleton-dependencies`
**Date**: 2026-09-25

## 1. Component Prop Signatures (JavaScript)

### `SeatGridCell` Props
```javascript
/**
 * @param {Object} props
 * @param {number} props.id - Seat primary key
 * @param {string} props.row - Row identifier (e.g. "A")
 * @param {number} props.seatNumber - Seat number within row (e.g. 1)
 * @param {string} props.section - Section identifier (e.g. "Section A")
 * @param {number} props.price - Ticket price
 * @param {'AVAILABLE' | 'LOCKED' | 'SOLD'} props.status - Operational seat status
 * @param {boolean} [props.isSelected] - Whether seat is currently selected by user
 * @param {Function} [props.onClick] - Callback when seat cell is clicked
 */
```

### `CountdownTimer` Props
```javascript
/**
 * @param {Object} props
 * @param {string | Date} [props.expiresAt] - ISO timestamp string or Date object when lease expires
 * @param {number} [props.initialSeconds] - Initial duration in seconds (fallback if expiresAt unset)
 * @param {Function} [props.onExpire] - Callback invoked when timer reaches 00:00
 */
```

### `Toast` Props
```javascript
/**
 * @param {Object} props
 * @param {string} props.message - Text message to render
 * @param {'success' | 'error' | 'info'} [props.type] - Notification variant theme
 * @param {Function} [props.onClose] - Callback when toast close button clicked or auto-dismissed
 * @param {number} [props.autoDismissMs] - Auto-dismiss delay in ms (default 4000)
 */
```

---

## 2. API Client Error Class Structure (`lib/api.js`)

```javascript
class ApiError extends Error {
  constructor(status, message, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status; // e.g. 401, 404, 409, 422
    this.data = data;     # Raw JSON payload from backend
  }
}
```

---

## 3. CSS Custom Properties Design System (`app/globals.css`)

```css
:root {
  /* Colors */
  --bg-dark: #0b0f19;
  --surface-dark: #111827;
  --surface-card: #1f2937;
  --border-glass: rgba(255, 255, 255, 0.1);
  --border-focus: #6366f1;
  
  /* Seat Status Colors */
  --seat-available: #10b981;
  --seat-available-hover: #059669;
  --seat-locked: #f59e0b;
  --seat-sold: #475569;
  --seat-selected: #06b6d4;

  /* Text & Accents */
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
  --text-muted: #6b7280;
  --accent-primary: #6366f1;
  --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  --error-crimson: #ef4444;

  /* Shadows & Glass */
  --glass-bg: rgba(17, 24, 39, 0.75);
  --glass-blur: blur(12px);
  --shadow-glow: 0 0 20px rgba(99, 102, 241, 0.25);
}
```
