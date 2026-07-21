# AI usage

How AI was used to build this project. This is the narrative; the underlying
prompts and full session log are in [`../prompts/`](../prompts/).

## Model

**Claude (Opus 4.8), by Anthropic**, in an agentic mode with a sandboxed Linux
container — so it could write files, install dependencies, and run commands and
tests during the session, not just emit code.

## Why this model

- **Two stacks, one session.** The backend (FastAPI/Python) and frontend
  (Next.js/TypeScript) were generated together and kept consistent — the
  frontend's API client types match the backend's response schemas exactly.
- **It ran what it wrote.** The backend test suite was executed (11 passing), a
  live server was smoke-tested end-to-end with `curl`, and the frontend was
  compiled to confirm it type-checks. That closed the loop between "looks right"
  and "works."
- **Edge-case discipline.** The brief's difficulty is in the edges, and the
  model produced a test for each rather than only the happy path.

## How AI was used, honestly

- **Design and architecture** were driven by prompts and steered by review — I
  chose the direction (e.g. random codes over sequential IDs, `307` over `301`
  for accurate click counting) and the model implemented and justified it.
- **All code** in `backend/` and `frontend/` was AI-generated, then run and
  tested in-session.
- **The tests** were AI-written and executed; I verified the assertions matched
  the intended behavior.
- **A real course-correction happened mid-build:** the initially pinned Next.js
  version carried a known security advisory, which was caught and bumped to a
  patched release before proceeding.
- **The docs** (planning notes, API reference, this file) were AI-drafted and
  reviewed for accuracy.

## What a reviewer should know

The value here wasn't autocomplete — it was delegating implementation while
keeping judgment on the decisions. Every non-obvious choice (duplicate handling,
redirect status code, code-generation strategy, route layout) is written up with
its alternatives and tradeoffs in [`planning.md`](planning.md), because those are
the parts worth a human's attention.
