# Snip — URL Shortener

A small full-stack URL shortener: paste a long URL, get a short code, and track
how many times each link is clicked.

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** Next.js (App Router) + React + TypeScript
- **Auth:** shared API key on create/list/stats; redirects are public

```
url-shortener/
├── backend/        FastAPI app + requirements
├── frontend/       Next.js dashboard
├── tests/          backend test suite (run from this root)
├── docs/           planning notes, API reference, AI-usage log
├── prompts/        AI tool prompts + session log (see AI usage below)
├── pytest.ini      test config (points pytest at backend/ + tests/)
└── README.md
```

## What it does

| Endpoint                  | Auth | Purpose                          |
| ------------------------- | ---- | -------------------------------- |
| `POST /api/shorten`       | ✅   | Long URL → short code            |
| `GET /{short_code}`       | —    | Redirect + count the click       |
| `GET /api/stats/{code}`   | ✅   | Click count for one code         |
| `GET /api/urls`           | ✅   | List all links (dashboard)       |
| `GET /health`             | —    | Liveness check                   |

Edge cases handled: invalid URLs (`422`), duplicate URLs (returns the existing
code), unknown codes (`404`), expired codes (`410`), and missing/bad API keys
(`401`). Full behavior in [`docs/API.md`](docs/API.md); the reasoning behind
each choice is in [`docs/planning.md`](docs/planning.md).

---

## Setup

Prerequisites: **Python 3.11+** and **Node 18+**.

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # then edit API_KEY to a secret of your choice
uvicorn app.main:app --reload
```

The API is now at `http://localhost:8000` (interactive docs at `/docs`).

Key environment variables (see `backend/.env.example`):

| Variable        | Default                      | Purpose                          |
| --------------- | ---------------------------- | -------------------------------- |
| `API_KEY`       | `dev-secret-key-change-me`   | Secret for the `X-API-Key` header |
| `DATABASE_URL`  | `sqlite:///./shortener.db`   | Where data is persisted          |
| `BASE_URL`      | `http://localhost:8000`      | Used to build full short links   |
| `CODE_LENGTH`   | `6`                          | Generated short-code length      |
| `CORS_ORIGINS`  | `http://localhost:3000`      | Allowed frontend origin(s)       |

### 2. Frontend

```bash
cd frontend
npm install

cp .env.local.example .env.local     # points at http://localhost:8000 by default
npm run dev
```

Open `http://localhost:3000`, paste your `API_KEY` into the **API key** field at
the top (it's saved in your browser), then shorten a link. The dashboard lists
your links and their click counts; open a short link in a new tab and hit
**Refresh** to watch the count go up.

### 3. Tests

Run from the `url-shortener/` root (the `pytest.ini` here wires the backend
`app` package onto the path and points pytest at `tests/`):

```bash
# from url-shortener/, with the backend venv active
pip install -r backend/requirements.txt   # includes pytest + httpx
pytest
```

11 tests cover auth, the happy path, click counting, and every edge case above.

---

## AI usage

This project was built with an AI coding tool as required. The model used and
the reasoning are documented in [`prompts/`](prompts/), along with the session
log. Short version: **Claude (Opus 4.8)** — chosen for strong multi-file code
generation, the ability to run and test the backend in-session, and careful
handling of the edge-case requirements.
