# API Specification v1.0

## Global Standards

- **Protocol:** HTTP/1.1 (Upgrade to HTTP/2 supported)
- **Base URL:** `https://api.atlas-search.com/v1`
- **Authentication:** Bearer Token (JWT) required for all write endpoints.
- **Rate Limiting:** Returned in headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`).

---

## 1. Search Pages

- **Endpoint:** `GET /search`
- **Use Case:** High-performance retrieval of indexed pages.

### Parameters

- `q` (string, required) — The search query (min 2 chars).
- `limit` (int, optional) — Results per page (default: 10, max: 100).
- `cursor` (string, optional) — Opaque cursor for next page (preferred over offset for performance).

### Response (200 OK)

```json
{
  "data": [
    {
      "id": "doc_123",
      "title": "Understanding API Design",
      "url": "https://example.com/api-design",
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
```

---

## 2. Request Re-crawl (On-Demand)

- **Endpoint:** `POST /crawl`
- **Use Case:** Triggers a high-priority crawl job.
- **SLA Note:** Requests here are pushed to the `high_priority` queue.

### Request Body

```json
{
  "url": "https://example.com/new-content",
  "depth": 1
}
```

### Response (202 Accepted)

We return `202 Accepted` because the crawl is asynchronous.

```json
{
  "job_id": "job_88a7b9c1",
  "status": "queued",
  "priority": "high",
  "estimated_completion": "2023-10-27T10:00:00Z"
}
```

### Error Responses

- `429 Too Many Requests` — if the user exceeds crawl quota.
- `400 Bad Request` — invalid URL format or malformed request body.

---

## 3. Get Job Status

- **Endpoint:** `GET /jobs/{job_id}`
- **Use Case:** Poll to check status of an on-demand crawl (1-hour SLA target).

### Response (200 OK - Processing)

```json
{
  "job_id": "job_88a7b9c1",
  "status": "processing",
  "result": null,
  "created_at": "2023-10-27T09:00:00Z"
}
```

### Response (200 OK - Completed)

```json
{
  "job_id": "job_88a7b9c1",
  "status": "completed",
  "result": {
    "url": "https://example.com/new-content",
    "indexed_terms": 450
  },
  "completed_at": "2023-10-27T09:02:15Z"
}
```

