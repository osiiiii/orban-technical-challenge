# Build session log

A faithful, chronological record of the AI session that produced this project —
from the initial build through the IDE setup and repository integration
follow-ups. Attach the raw chat export alongside this file (see `README.md`).

**Tool / model:** Claude (Opus 4.8), agentic mode with a sandboxed Linux
container (file editing + shell + ability to run tests).

---

## Prompt 1 — Build the project (verbatim, condensed)

> Build a URL Shortener: takes long URLs, generates short codes, redirects
> users, and tracks click counts.
> **Backend (FastAPI + Python):** create endpoint, public redirect endpoint,
> stats endpoint, API-key auth for creating, SQLite persistence, handle edge
> cases (duplicate URLs, invalid URLs, expired/missing codes).
> **Frontend (Next.js + React):** form to shorten a URL, dashboard of created
> URLs + click counts, loading and error states.
> **Testing:** a few meaningful backend tests.
> **Docs:** API docs + setup guide.
> **AI usage (mandatory):** use AI tools, include the full transcript in
> `/prompts/`, state which model(s) and why.
> **Also:** a `/docs/` folder with planning notes showing the thinking before
> the code.

### Plan worked to

1. Read the frontend design guidance before building any UI.
2. Backend first, in dependency order: `config → database → models → schemas →
   auth → crud → main`.
3. Write the tests and **run them** before touching the frontend.
4. Smoke-test a live server with `curl`.
5. Build the frontend (typed API client → components → page) and **compile it**.
6. Write planning notes, API reference, README/setup, and the AI-usage log.

### What happened

1. Scaffolded the tree: `backend/{app,tests}`, `frontend/{app,components,lib}`,
   `docs/`, `prompts/`.
2. Wrote the backend modules:
   - `config.py` — env-driven settings via `pydantic-settings`.
   - `database.py` — SQLAlchemy engine/session; SQLite `check_same_thread`.
   - `models.py` — `URL` table: unique-indexed `short_code`, indexed
     `long_url`, `click_count`, `created_at`, nullable `expires_at`,
     `is_expired` property.
   - `schemas.py` — `AnyHttpUrl` validation so invalid URLs 422 automatically.
   - `auth.py` — `X-API-Key` dependency with a constant-time compare.
   - `crud.py` — random base62 code generation with a uniqueness retry;
     idempotent duplicate handling; atomic click increment at the DB.
   - `main.py` — routes under `/api/...` plus the public catch-all redirect at
     `/{short_code}`; CORS; `307` redirect so browsers don't cache and skip
     counting.
3. Wrote 11 tests over an in-memory SQLite DB (`StaticPool`): auth required /
   wrong key, create returns a code, redirect resolves + counts clicks, stats
   shape, list, invalid URL → 422, missing code → 404, duplicate URL → same
   code, expired code → 410, expiry sets a future timestamp.
4. Ran `pytest -q` → **11 passed**.
5. Live smoke test with `uvicorn` + `curl`: create (401 w/o key, 201 with) →
   redirect (`307`, correct `Location`) → second redirect → stats showing
   `click_count: 2` → unknown code `404`. All correct.
6. Built the frontend: typed `lib/api.ts`, `globals.css` tokens, `ShortenForm`
   and `UrlDashboard` with idle/loading/error/empty states, `page.tsx` with
   API-key persistence in `localStorage`.
7. **Course-correction:** first `npm install` pinned `next@14.2.15`, flagged for
   a security vulnerability. Bumped to patched `next@14.2.35` and reinstalled.
8. `npm run build` → compiled successfully, types valid.
9. Wrote `docs/planning.md`, `docs/API.md`, `README.md`, and the prompts log.

### Notable decisions surfaced

- Random base62 codes over sequential-id encoding — keeps codes non-enumerable.
- Duplicate long URLs return the existing code (idempotent).
- `307` redirect over `301`/`302` so repeat visits aren't served from cache and
  every click is counted.
- A `click_count` column rather than a per-hit events table — enough for the
  brief; events-table upgrade path noted for future analytics.

(Full reasoning: `../docs/planning.md`.)

---

## Prompt 2 — Run both halves in PyCharm 2026.1.2

> steps to build and run both backend and frontend in pycharm 2026.1.2

Confirmed via search that PyCharm 2026.1 is a single unified product and that
JS/TS/npm-script support moved into the free core tier, so both halves run in
one window without a Pro subscription. Provided: one-time setup (open project,
create `backend/.venv`, install `requirements.txt`, set Node, `npm install`),
a **Python module** run config for the backend (`module: uvicorn`, params
`app.main:app --reload`, working dir = `backend`), an **npm** run config for the
frontend (`run` → `dev`), and an optional **Compound** config to launch both.

---

## Prompt 3 — How to create the env files

> details on how to do this: copy `backend/.env.example` → `backend/.env` (set
> `API_KEY`); copy `frontend/.env.local.example` → `frontend/.env.local`.

Clarified that the API key lives **only** in the backend env; the frontend file
just holds `NEXT_PUBLIC_API_BASE`. Gave PyCharm copy/paste steps and terminal
equivalents (`cp` for macOS/Linux, `Copy-Item` for PowerShell), a
`secrets.token_urlsafe(32)` one-liner to generate the key, and a reminder to
avoid stray quotes/whitespace around the value.

---

## Prompt 4 — "backend" run config error

> Error running "backend": Cannot start a process, the working directory
> '…\url-shortener\backend' does not exist

The `…` placeholder from the instructions had been pasted in literally.
Fix: set the Working directory to the real absolute path, or use the
`$ProjectFileDir$/backend` macro so it resolves on any machine. Noted that a
wrong working dir also shows up later as `ModuleNotFoundError: app`.

---

## Prompt 5 — Add the project to an existing GitHub repo

> Add this url-shortener to an existing `notes-app` repo so the final layout has
> both projects side by side, plus `resume.pdf` and a top-level `README.md`.
> Target: `url-shortener/{docs,prompts,backend,frontend,tests}`. Make it
> **incremental, meaningful commits** — not one big push — with clear messages.
> Also update `prompts/README.md` and `prompts/session-log.md`.

### What happened

1. **Restructured to the target layout:** moved `backend/tests/` up to a
   top-level `url-shortener/tests/`, removed `tests/__init__.py`, and added a
   `pytest.ini` (`pythonpath = backend`, `testpaths = tests`) so the suite
   resolves the `app` package from its new location.
2. **Verified:** ran `pytest` from the `url-shortener/` root → **11 passed**.
3. **Docs:** added `docs/ai-usage.md` (the AI-usage narrative) and updated the
   README's test command to run from the project root.
4. **Prompts:** updated this log and `prompts/README.md` to cover Prompts 2–5.
5. Provided a commit-by-commit git workflow (backend → tests → frontend → docs →
   prompts → config → resume → top-level README) rather than a single commit.
