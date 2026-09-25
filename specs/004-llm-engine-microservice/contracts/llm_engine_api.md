# API Contract Specification: LLM Engine Microservice

**Feature Branch**: `004-llm-engine-microservice`
**Date**: 2026-09-25

## Base URL
`http://localhost:8001` (or `http://llm-engine:8001` in Docker networks)

---

## 1. Parse Natural Language Query

### Endpoint
`POST /api/v1/parse-query`

### Purpose
Parses a natural language search prompt and extracts structured ticket search parameters (`quantity`, `adjacency`, `max_price`, `preferred_section`).

### Request Headers
| Header | Value | Required | Description |
| :--- | :--- | :--- | :--- |
| `Content-Type` | `application/json` | Yes | Payload format |

### Request Body
```json
{
  "query": "Find me 2 seats together in Section A under $150"
}
```

### Success Response (HTTP 200 OK)
```json
{
  "quantity": 2,
  "adjacency": true,
  "max_price": 150.0,
  "preferred_section": "Section A"
}
```

### Partial / Minimal Query Response (HTTP 200 OK)
```json
{
  "quantity": 1,
  "adjacency": false,
  "max_price": null,
  "preferred_section": null
}
```

### Validation Error Response (HTTP 422 Unprocessable Entity)
```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 2. Microservice Health Check

### Endpoint
`GET /health`

### Purpose
Liveness probe for backend readiness and container monitoring.

### Success Response (HTTP 200 OK)
```json
{
  "status": "healthy",
  "provider": "gemini"
}
```
