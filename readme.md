# Projects

Two self-contained projects live in this repository. Each has its own README,
docs, and setup steps inside its folder.

```
/
├── notes-app/        A notes application
├── url-shortener/    A URL shortener with click tracking
├── resume.pdf
└── README.md         (this file)
```

## url-shortener

A full-stack URL shortener: paste a long URL, get a short code, and track how
many times each link is clicked.

- **Stack:** FastAPI + SQLAlchemy + SQLite (backend), Next.js + React +
  TypeScript (frontend).
- **Auth:** a shared API key protects create/list/stats; redirects are public.
- **Approach:** the core is a lookup table with a counter, so the real work is
  in the edges — duplicate URLs return the existing code, invalid URLs 422,
  missing codes 404, expired codes 410, and redirects use `307` (not `301`) so
  browsers don't cache them and silently skip click counting. Every decision,
  its alternatives, and its tradeoffs are written up in
  [`url-shortener/docs/planning.md`](url-shortener/docs/planning.md).
- **Tested:** 11 backend tests covering auth, click counting, and each edge
  case. Frontend compiles and type-checks.
- **Built with AI:** see [`url-shortener/docs/ai-usage.md`](url-shortener/docs/ai-usage.md)
  for how, and [`url-shortener/prompts/`](url-shortener/prompts/) for the
  prompts and session log.

Setup and API reference: [`url-shortener/README.md`](url-shortener/README.md).

## notes-app

<!-- TODO: fill this in with the same shape as above. -->
A notes application.

- **Stack:** _describe backend / frontend here._
- **Approach:** _one or two sentences on the design and the key decisions._
- **Tested:** _what the tests cover._

Setup: [`notes-app/README.md`](notes-app/README.md).

## A note on approach across both

<!-- TODO: a short paragraph tying the two together — how you scoped each
     problem, where you spent effort vs. kept things simple, and how you used
     AI as a tool while keeping judgment on the design decisions. -->
