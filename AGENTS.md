# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Intelligo is becoming a web app for translating Asian web novel chapters into English — *a reading room that happens to translate*. The product vision lives in `DESIGN_SPEC.md`; treat that document as the source of truth for frontend tone, scope, naming, and roadmap.

This branch (`ui-rewrite`) is mid-rewrite. The previous incarnation was a CLI built around Trafilatura, a Korean prompt, and a self-building glossary. That code has been deleted. The repo is being rebuilt around a FastAPI backend in `api/` and an eventual Next.js frontend (not yet started).

## Repo layout

```
api/                FastAPI backend — the only running code right now
  main.py           app, lifespan, route handlers
  db.py             sqlite connection + schema
  schemas.py        Pydantic request/response models
  translator.py     OpenRouter call
  requirements.txt
  .env.example
DESIGN_SPEC.md      Frontend design spec — canonical for visual + product direction
mockup.html         Static design mockup
mockup.css
testform.html       Scratch HTML form for hitting the API by hand
```

There is no test suite, lint config, or build step. Don't invent commands for them.

## Running the API

```bash
python -m venv .venv && source .venv/bin/activate
cd api
pip install -r requirements.txt
cp .env.example .env   # then add OPENROUTER_API_KEY
uvicorn main:app --reload
```

The sqlite database (`api/intelligo.db`) is created on first launch from the schema in `db.py`. It's gitignored; deleting it is a clean reset.

## API surface (current)

| Method | Path                | Status                                                                                       |
| ------ | ------------------- | -------------------------------------------------------------------------------------------- |
| GET    | `/api/series`       | implemented — `?id=<uuid>` lookup, 404 if missing                                            |
| POST   | `/api/series`       | implemented — JSON `{name}`, 400 if name > 150 chars                                         |
| POST   | `/api/translations` | partial — `chapterBody` (text) translates via OpenRouter; `chapterFile` returns 501 for now  |

`/api/translations` is a multipart form endpoint with **camelCase aliases on the wire** (`seriesId`, `chapterNumber`, `chapterBody`, `chapterFile`, `overwriteChapterIfExists`) — Python params stay snake_case but the alias is what clients send. Keep that distinction when adding fields.

## Architecture

The backend is a flat FastAPI app — no routers, no service layer, no DI framework. Four files, one job each:

- **`main.py`** — owns the app, the lifespan (opens/closes the sqlite connection on `app.state.db`), and every route handler.
- **`db.py`** — returns a connection with the schema applied. Schema is idempotent (`CREATE TABLE IF NOT EXISTS`).
- **`schemas.py`** — Pydantic models. The wire contract for JSON endpoints.
- **`translator.py`** — wraps the OpenRouter call. Model and temperature are constants in this file, not config; change them here.

Translations currently run synchronously in the request handler. `DESIGN_SPEC.md` §5.4 describes a "press" — a queue with human-voiced status updates the frontend polls — but no async job machinery exists yet.

## Conventions worth knowing

- **One sqlite connection** lives on `app.state.db`, opened in lifespan. `check_same_thread=False` is required because FastAPI runs sync handlers on a thread pool. SELECTs do not need `commit()`.
- **OpenRouter, not OpenAI.** The `openrouter` PyPI package is what we use; don't swap to the OpenAI SDK without a reason.
- **`.env` lives in `api/`**, not the repo root. `load_dotenv()` is called from `api/main.py` and resolves it via cwd, which is why the run instructions `cd api` first.
- **`*.db` is gitignored.** The sqlite file is local-only and disposable.

## What's deliberately not here yet

The CLI handled scraping (Trafilatura + per-hostname dispatch), Korean-specific prompts, a self-building glossary persisted to JSON, and previous-chapter context injection. None of that has been ported. When wiring those features back in, read `DESIGN_SPEC.md` first — the glossary in particular is reframed as the **Card Catalog** and is meant to be a first-class artifact, not a hidden file.
