My submission for the Orban Labs Backend Developer Tech Challenge

```
/
├── notes-app/        A notes application (built by hand by Daniel Osi)
├── url-shortener-ai-assisted/    A URL shortener with click tracking (built with AI - Claude Opus 4.8)
├── resume.pdf
└── README.md         
```

## url-shortener

A full-stack URL shortener: paste a long URL, get a short code, and track how
many times each link is clicked. (built with AI - Claude Opus 4.8)

Setup and API reference: [`url-shortener-ai-assisted/README.md`](url-shortener-ai-assisted/README.md).

## notes-app

A notes application  (built by hand by Daniel Osi).

Setup: [`notes-app/README.md`](notes-app/README.md).

## A note on approach across both

notes-app (built by hand)

A notes API with a Next frontend built on FastAPI + SQLite on :8000, Next on :3000 that just calls it. Full CRUD plus search (keyword hits title/body, tag match is exact) behind one shared API key; /health is open,everything under /notes needs the key...tags are a JSON array right on the note row instead of a join table: keyword search runs in SQL. The tag filter runs in Python after ,totally fine at this size, and normalizing tags into their own table is the one thing I'd change if it ever got big.Kept it deliberately boring, like the brief asked (twice): no accounts, no migrations (tables build on startup), no pagination, none of it needed here. Schemas are split into create/update/out so clients can't set an id or timestamp, errors are all one flat {detail} string, and the API key never touches the browser. The frontend calls a server-side proxy that adds it. Tests cover the stuff that actually breaks: auth, blank title, a full CRUD run, and search, each on a fresh in-memory db.Something worth knowing: /notes/search has to be declared before /notes/{id} or FastAPI swallows it as an id.

Setup: notes-app/README.md.

url-shortener (bult with AI including this note)

A full-stack URL shortener that turns long URLs into short codes, redirects visitors to the original destination, and tracks how many times each link is clicked. A FastAPI backend handles creation, redirection, and stats; a Next.js frontend provides a form and a dashboard on top of it.

Stack. FastAPI + SQLAlchemy + SQLite on the backend, Next.js (App Router) + React + TypeScript on the frontend. Data persists to a single SQLite file, and because everything goes through SQLAlchemy, moving to Postgres later is a connection-string change rather than a rewrite.

Auth. Creating, listing, and inspecting links requires a shared secret sent in the X-API-Key header, compared in constant time to avoid a timing side channel. Redirects are deliberately public so short links work for anyone.

The design decisions that matter. The core is a lookup table with a counter, so the real engineering is in the edges:

Non-enumerable short codes. Codes are random base62 with a uniqueness check rather than an encoded auto-increment id, so nobody can walk the ID space and read every destination.
Idempotent duplicates. Submitting a URL that already has an active short link returns the existing code instead of minting a new one, keeping the table clean and repeated clicks of a "shorten" button harmless.
307 redirects, not 301. A permanent redirect gets cached by the browser, which would let repeat visits skip the server and silently undercount clicks — so redirects use a temporary 307 and every visit is counted. The counter itself is incremented atomically in SQL, not read-modify-write in Python.
Route layout. The redirect lives at the catch-all /{short_code}, so every real endpoint is namespaced under /api/... (plus /health) to guarantee no code can ever shadow an API route.
A counter column, not an events table. The brief only asks for a count, so each URL carries a click_count rather than one row per hit. The events-table upgrade path — for time-series and referrer analytics — is noted for later.

Edge cases. Invalid URLs return 422 (validated by Pydantic's AnyHttpUrl before any handler runs), unknown codes 404, expired codes 410 Gone, and missing or wrong API keys 401. Each has a matching test.

Tested. 11 backend tests over an in-memory SQLite database cover auth, the full happy path, click counting, and every edge case above; the running server was also smoke-tested end-to-end (create → redirect → count → stats). The frontend compiles and type-checks clean.

Frontend. A single page with three cards — API key, shorten form, and a dashboard listing links with live click counts. Every async action has explicit idle / loading / error / empty states, the key is stored only in the browser, and a security advisory on the initially pinned Next.js version was caught and patched during the build.

Every decision, its alternatives, and its tradeoffs are written up in url-shortener-ai-assisted/docs/planning.md; the API reference is in url-shortener-ai-assisted/docs/API.md; how AI was used is in url-shortener-ai-assisted/docs/ai-usage.md with the prompts and session log in url-shortener-ai-assisted/prompts/. Setup: url-shortener-ai-assisted/README.md.


A note on approach across both

Two take-homes, same instinct: find where the difficulty actually lives and spend the effort there. Both briefs said "keep it simple," so the hard part was restraint — one API key instead of accounts, create-tables-on-startup instead of migrations, a counter instead of an events table. The interesting work sat in the edges: route ordering and tag search in notes-app, redirect caching and non-enumerable codes in the shortener. AI wrote most of the code and wrote it fast, but the calls about what to build, what to skip, and why — 307 over 301, JSON tags over a join table — were mine, and they're documented so you can audit the reasoning, not just the output.
