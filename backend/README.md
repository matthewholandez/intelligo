# Intelligo — Backend

A FastAPI server that handles novels, chapters, the per-novel glossary, and the
translation pipeline. Data lives in a local SQLite database (`novels.db`), and
finished translations are also written to disk as Markdown.

## Stack

- **FastAPI** — HTTP API (interactive docs at `/docs`)
- **SQLModel** over **SQLite** (`novels.db`, created on first run)
- **LangChain** + [`langchain-openrouter`](https://pypi.org/project/langchain-openrouter/) — LLM access via [OpenRouter](https://openrouter.ai/)
- **trafilatura** — extracts readable text from uploaded HTML
- **[`uv`](https://docs.astral.sh/uv/)** — dependency & environment management (Python 3.12)

## Setup

```bash
uv sync
export OPENROUTER_API_KEY=...    # required for translation
uv run fastapi dev               # http://127.0.0.1:8000  (docs at /docs)
```

### Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | yes | Authenticates LLM calls to OpenRouter |
| `OPENROUTER_API_BASE` | no | Override the OpenRouter API base URL |
| `OPENROUTER_APP_TITLE` / `OPENROUTER_APP_URL` | no | Attribution headers sent to OpenRouter |

The translation model is configured in `app/translation.py` (`MODEL`, currently
`google/gemini-2.5-flash`).

## How translation works

When a chapter is uploaded (`POST /novels/{novel_id}/chapters`), two LLM agents
run in sequence:

1. **Extract** — if an `.html` file is provided, readable text is extracted with
   trafilatura; if `source_text` is provided instead, it is used as-is.
2. **Term-extraction agent** — reads the chapter and returns new glossary terms
   (proper nouns, character names, factions, titles, skills, realms, key items)
   as structured output (`GlossaryExtraction`). The novel's existing terms are
   passed in so they aren't re-proposed. New terms are merged into the glossary
   with **first-write-wins** semantics (existing entries are never overwritten).
3. **Build context** — the chapter is scanned **deterministically** for the
   glossary terms it mentions (`scan_existing`); those — including the terms just
   added — become the translation context.
4. **Translation agent** — translates the chapter using that glossary context so
   canonical translations are reused verbatim, returning `TranslatedChapter`.
5. **Persist** — the chapter is saved to the database and the translation is
   written to `translations/<novel_id>/chapter-NNNN.md`.

The whole pipeline runs **synchronously** within the upload request.

## Project layout

```
app/
  main.py          # FastAPI app + router registration
  db.py            # SQLite engine, session dependency, startup lifespan
  types.py         # SQLModel tables + Pydantic schemas (incl. LLM structured output)
  extraction.py    # HTML -> text via trafilatura
  translation.py   # prompt building, LLM call, write-to-disk
  glossary.py      # load / format-for-prompt / merge-updates helpers
  routers/
    novels.py      # CRUD for novels
    chapters.py    # CRUD + upload/translate pipeline
    glossary.py    # CRUD for glossary entries
novels.db          # SQLite database (gitignored / created on first run)
translations/      # generated Markdown output, per novel
```

## API

Interactive docs at `/docs` when the server is running.

### Novels

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/novels` | List novels. Query: `offset` (default `0`), `limit` (default/max `100`) |
| `GET` | `/novels/{novel_id}` | Get a novel — `404` if missing |
| `POST` | `/novels` | Create a novel — body `NovelCreate` |
| `PATCH` | `/novels/{novel_id}` | Update a novel (partial) — `404` if missing |
| `DELETE` | `/novels/{novel_id}` | Delete a novel — `404` if missing |

### Chapters

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/novels/{novel_id}/chapters` | Upload & translate a chapter (see below) |
| `GET` | `/novels/{novel_id}/chapters` | List chapters ordered by `number` — `404` if novel missing |
| `GET` | `/novels/{novel_id}/chapters/{chap_id}` | Get a chapter — `404` if missing |
| `PATCH` | `/novels/{novel_id}/chapters/{chap_id}` | Update a chapter (partial) — `404` if missing |
| `DELETE` | `/novels/{novel_id}/chapters/{chap_id}` | Delete a chapter — `404` if missing |

**Upload** accepts `multipart/form-data`:

- `number` (int, required)
- `file` (`UploadFile`, optional) — must be `.html`, valid UTF-8, max 5 MB; text is extracted via trafilatura
- `source_text` (str, optional) — used verbatim

Provide **exactly one** of `file` or `source_text`. Responses: `200`
`ChapterPublic`; `400` bad input; `404` novel missing; `413` file over 5 MB.

### Glossary

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/novels/{novel_id}/glossary` | List entries ordered by `source_term` — `404` if novel missing |
| `POST` | `/novels/{novel_id}/glossary` | Add an entry — body `GlossaryEntryCreate`; `409` on duplicate term |
| `GET` | `/novels/{novel_id}/glossary/{entry_id}` | Get an entry — `404` if missing |
| `PATCH` | `/novels/{novel_id}/glossary/{entry_id}` | Update an entry (partial); `409` on duplicate term |
| `DELETE` | `/novels/{novel_id}/glossary/{entry_id}` | Delete an entry — `404` if missing |

Glossary entries are unique per `(novel_id, source_term)`.

## Schemas

`NovelPublic` — `id` (int), `name` (str), `updated_on` (datetime)

`ChapterPublic` — `id` (int), `novel_id` (int), `number` (int),
`source_text` (str), `translated_text` (str | null), `updated_on` (datetime)

`GlossaryEntryPublic` — `id` (int), `novel_id` (int), `source_term` (str),
`translation` (str), `created_on` (datetime)

`*Create` / `*Update` bodies accept the writable fields; `Update` bodies are
partial (only provided fields are modified).
</content>
