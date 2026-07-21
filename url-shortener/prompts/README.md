# AI usage

This project was built end-to-end with an AI coding assistant, as required by
the brief. This folder is the "receipts": the model used, why, and every prompt
that shaped the project.

## Model used

**Claude (Opus 4.8), by Anthropic**, running in an agentic environment with a
sandboxed Linux container (able to write files, install dependencies, and run
commands/tests during the session).

## Why this model

- **Multi-file code generation with a real toolchain.** The task spans a Python
  backend and a TypeScript/Next.js frontend. Opus handled both stacks in one
  session and kept them consistent (the frontend's API client matches the
  backend's response shapes exactly).
- **It could actually run the code, not just write it.** During the build the
  backend test suite was executed (11 passing), a live server was smoke-tested
  with `curl` (create → redirect → click count → stats), and the frontend was
  compiled with `npm run build` to confirm it type-checks.
- **Careful with the edge cases.** The brief's real weight is in the edges
  (duplicates, invalid URLs, expired/missing codes, the redirect-vs-API route
  collision). Opus reasoned through each and produced a matching test.

## What's in this folder

- `session-log.md` — a structured, chronological log of the whole session:
  every prompt (the initial build plus the follow-ups on IDE setup and repo
  integration), the plan worked to, the concrete steps taken, commands run,
  results, and the course-corrections along the way.
- The **raw chat export** from the AI tool should be attached here alongside the
  log as `raw-transcript.md` / `raw-transcript.txt`. (An assistant can't export
  the host chat from inside itself — export it from the tool's UI and drop it
  in.)

A higher-level narrative of *how* AI was used across the project lives in
[`../docs/ai-usage.md`](../docs/ai-usage.md); this folder holds the underlying
prompts and log it draws from.
