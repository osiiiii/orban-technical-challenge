# API reference

Base URL (default): `http://localhost:8000`

Interactive docs are generated automatically by FastAPI:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

Creating, listing, and inspecting links requires an API key sent in the
`X-API-Key` header. The key must match `API_KEY` in the backend environment.
**Redirects are public** and need no key.

```
X-API-Key: your-secret-key
```

A missing or wrong key returns `401 Unauthorized`.

---

## `POST /api/shorten`

Create a short URL. **Auth required.**

**Request body**

| Field             | Type            | Required | Notes                                    |
| ----------------- | --------------- | -------- | ---------------------------------------- |
| `long_url`        | string (URL)    | yes      | Must be a valid `http`/`https` URL.      |
| `expires_in_days` | integer \| null | no       | Positive. Omit/`null` = never expires.   |

**Example**

```bash
curl -X POST http://localhost:8000/api/shorten \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{"long_url": "https://example.com/a/long/path", "expires_in_days": 30}'
```

**`201 Created`**

```json
{
  "short_code": "7Tw4wW",
  "short_url": "http://localhost:8000/7Tw4wW",
  "long_url": "https://example.com/a/long/path",
  "click_count": 0,
  "created_at": "2026-07-21T08:17:49.154653Z",
  "expires_at": "2026-08-20T08:17:49.154653Z"
}
```

Submitting a URL that already has an active short link returns that existing
link (still `201`) rather than creating a duplicate.

**Errors:** `401` (bad key), `422` (invalid URL or non-positive expiry).

---

## `GET /{short_code}`

Resolve a short code and redirect to the original URL. **Public.** Increments
the click counter on every successful hit.

```bash
curl -i http://localhost:8000/7Tw4wW
```

**`307 Temporary Redirect`** with a `Location` header pointing at the original
URL. (307 is used rather than 301 so browsers don't cache the redirect and
silently skip click counting.)

**Errors:** `404` (unknown code), `410 Gone` (code has expired).

---

## `GET /api/stats/{short_code}`

Return the click count and metadata for one code. **Auth required.**

```bash
curl http://localhost:8000/api/stats/7Tw4wW -H "X-API-Key: your-secret-key"
```

**`200 OK`**

```json
{
  "short_code": "7Tw4wW",
  "long_url": "https://example.com/a/long/path",
  "click_count": 12,
  "created_at": "2026-07-21T08:17:49.154653Z",
  "expires_at": "2026-08-20T08:17:49.154653Z",
  "is_expired": false
}
```

**Errors:** `401` (bad key), `404` (unknown code).

---

## `GET /api/urls`

List every created link, newest first. Powers the dashboard. **Auth required.**

```bash
curl http://localhost:8000/api/urls -H "X-API-Key: your-secret-key"
```

**`200 OK`** — an array of the same objects returned by `POST /api/shorten`.

---

## `GET /health`

Liveness check. **Public.** Returns `{"status": "ok"}`.

---

## Status codes at a glance

| Code  | Meaning                                             |
| ----- | --------------------------------------------------- |
| `200` | OK (stats, list, health)                            |
| `201` | Link created (or existing duplicate returned)       |
| `307` | Redirect to the original URL                        |
| `401` | Missing or invalid API key                          |
| `404` | Short code not found                                |
| `410` | Short code has expired                              |
| `422` | Invalid request body (bad URL, bad expiry)          |
