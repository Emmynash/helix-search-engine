# API Specification v1.0

## Global Standards
- **Protocol:** HTTP/1.1 (Upgrade to HTTP/2 supported)
- **Base URL:** `https://api.helix-search.com/v1`
- **Authentication:** Bearer Token (JWT) required for all write endpoints.
- **Rate Limiting:** Returned in headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`).

---

## 1. Search Pages
**Endpoint:** `GET /search`

**Use Case:** High-performance retrieval of indexed pages.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `q` | string | Yes | The search query (min 2 chars). |
| `limit` | int | No | Results per page (default: 10, max: 100). |
| `cursor` | string | No | Opaque string for next page (Performance: better than offset). |

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "doc_123",
      "title": "Understanding API Design",
      "url": "[https://example.com/api-design](https://example.com/api-design)",
      "snippet": "API design is crucial for...",
      "score": 0.98
    }
  ],
  "meta": {
    "total_hits": 15400,
    "next_cursor": "cXdlcnR5MTIzNDU=",
    "execution_time_ms": 12
  }
}