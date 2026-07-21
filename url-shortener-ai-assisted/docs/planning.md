# Planning notes

Written before and during the build. This is the thinking, not the polish.

## 1. What is actually being asked

Strip the brief down to verbs and nouns:

- **Create** a short code from a long URL (protected by an API key).
- **Redirect** a visitor who hits a short code to the original URL (public).
- **Count** how many times each code has been used.
- **Report** that count back on request.
- **Persist** everything to SQLite.
- **Survive** bad input: duplicate URLs, invalid URLs, expired/missing codes.

Plus a small frontend (form + dashboard with loading/error states), a few
backend tests, docs, and the AI-usage paperwork.

The core is tiny — it's a lookup table with a counter. The interesting work is
entirely in the edges: what a "duplicate" means, what happens at an expired or
missing code, how the API key is checked, and how the redirect route avoids
colliding with the API routes. So most of the planning below is about edges.

## 2. Shape of the system

```
 Browser (Next.js)                    FastAPI                 SQLite
 ────────────────                    ────────                ────────
  API-key bar  ─┐
  Shorten form ─┼─ POST /api/shorten ─▶ auth ─▶ crud.create ─▶ urls table
  Dashboard    ─┘  GET  /api/urls    ─▶ auth ─▶ crud.list
                   GET  /api/stats/{code} ─▶ auth ─▶ crud.get

  Visitor ───────▶ GET  /{code} (public) ─▶ resolve ─▶ 307 ─▶ long_url
                                             └─ increment click_count
```

One table, four routes, one dependency for auth. Kept the data-access logic in
a `crud.py` module so the route handlers stay thin and the tests can call the
same functions the API uses.

## 3. Decisions and the alternatives I weighed

### Short-code generation — random base62, not a sequential counter

Two obvious options:

1. **Encode the row's auto-increment id in base62.** Guaranteed unique, shortest
   possible codes, no collision checks. But codes become sequential and
   *enumerable* — `abc`, `abd`, `abe`… anyone can walk the whole table and read
   every destination. For a link shortener that's a real privacy leak.
2. **Random base62 with a uniqueness check.** Codes aren't guessable. Cost is a
   possible collision, but at length 6 that's 62⁶ ≈ 56 billion combinations, so
   collisions are astronomically rare; I retry on the off chance and widen the
   code as a last resort.

Chose (2). The non-enumerability is worth the tiny extra lookup. Tradeoff: codes
are one char longer than a pure counter would need at low volumes, and there's a
theoretical (never-observed) retry cost as the table fills.

### Duplicate URLs — return the existing code (idempotent)

When the same long URL is submitted twice, I return the existing active mapping
instead of minting a new code. Rationale: it keeps the table clean and makes the
shorten operation idempotent, which is the least surprising behavior for a
"shorten this" button someone might click twice.

Tradeoff: you can't have two different short codes point at the same
destination, which some products deliberately support (e.g. per-campaign links
to the same page). If that were a requirement I'd add an explicit
`allow_duplicate` flag or custom-alias support. Noted, not built.

### Click counting — a counter column, not an events table

The brief only asks for a count, so a single `click_count` integer that I bump
atomically (`SET click_count = click_count + 1` in the DB, not read-modify-write
in Python) is enough and cheap.

Alternative: a separate `clicks` table with one row per hit (timestamp,
referrer, user-agent). That unlocks time-series and geo/referrer analytics but
is overkill here and makes every redirect an insert. I went with the counter and
left a note in the code about where the events table would slot in if analytics
became a requirement.

### Redirect status code — 307, not 301/302

- **301 (permanent)** is what "real" shorteners often use for SEO, but browsers
  *cache* it aggressively — after the first hit the browser may skip the server
  entirely on repeat visits, which would silently undercount clicks. Bad for a
  product whose whole job is counting clicks.
- **307 (temporary)** isn't cached by default, so every visit comes back through
  the server and gets counted. Chose 307. Tradeoff: slightly slower repeat
  visits and no SEO link-equity, both acceptable for this use case.

### Route layout — API under `/api`, redirect at the root

The redirect has to live at `/{short_code}` to be a genuinely short link. That's
a greedy catch-all, so everything else (shorten, stats, list, health) is
namespaced under `/api/...` and `/health` to guarantee no code can ever shadow a
real endpoint.

### Auth — shared API key in a header, constant-time compare

The brief says "simple authentication via API key," so I didn't reach for OAuth
or JWT. One shared secret in `X-API-Key`, compared with `secrets.compare_digest`
to avoid a timing side-channel. Redirects skip the dependency entirely so they
stay public.

Tradeoff: a single shared key means no per-user link ownership — the dashboard
shows *all* links, not "mine." Real multi-tenant ownership would need user
accounts and a `user_id` foreign key. Out of scope, called out here.

### Validation — let Pydantic reject bad URLs

`long_url` is typed as `AnyHttpUrl`, so FastAPI returns a 422 with a clear
message before my code runs. No hand-rolled regex. Expiry is an optional
positive-integer day count rather than a raw timestamp, which is friendlier for
the form and impossible to set in the past.

## 4. Edge-case matrix (what each failure returns)

| Situation             | Behavior                                   |
| --------------------- | ------------------------------------------ |
| Missing/invalid API key | `401` on create/list/stats               |
| Invalid URL           | `422` with a validation message            |
| Duplicate URL         | `201` returning the existing code          |
| Unknown short code    | `404` on redirect and stats                |
| Expired short code    | `410 Gone` on redirect                     |
| Valid redirect        | `307` to the target, click count += 1      |

Each row has a corresponding test.

## 5. Frontend approach

Deliberately small: a single page with three cards — API key, shorten form,
dashboard. State is plain React (`useState`/`useEffect`); no data-fetching
library, since there are exactly two calls. The API key lives in `localStorage`
so a refresh doesn't lose it. Every async action has three states — idle,
loading (spinner / disabled button), and error (inline banner in the
interface's own voice). After a successful create I optimistically prepend the
new row and then refetch so the click counts stay authoritative.

Design: a cool, technical light theme with monospace short codes — the code
*is* data, so it's set in mono everywhere. Avoided the warm-cream/serif/
terracotta look that reads as a default. One signature: the hero strip that
shows a long URL visibly compressing into a short chip.

## 6. What I'd do next with more time

- Custom aliases and an explicit "new code for same URL" path.
- A real `clicks` events table for time-series and referrer analytics.
- User accounts so the dashboard is per-owner instead of global.
- Rate limiting on create, and an Alembic migration instead of
  `create_all` at startup.
- QR codes for each short link.
