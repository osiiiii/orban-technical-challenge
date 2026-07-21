# Notes API + Clientside

A small notes app: a FastAPI + SQLite backend using an
authenticated CRUD API with search functionality.. and a Next.js client that lists, searches,
creates, edits & deletes notes.

Default API key is `dev-key-change-me` (set in `.env`). Every `/notes`
request must include it in the `X-API-Key` header.

To run the tests:

```bash
cd backend
source .venv/bin/activate
pytest
```

I wrote ten tests cover the CRUD lifecycle, authentication, input validation, and
search. See [`docs/planning.md`](docs/planning.md) for what each group proves. Tried to keep things simple and basic too.