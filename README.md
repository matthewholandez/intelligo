<div align="center">
    <br/>
    <h1>Intelligo</h1>
    <h3>Translate your favourite Asian web novels to English</h3>
</div>

![Python 3.11+](https://img.shields.io/badge/python-%3E=3.11-blue?logo=python)

Intelligo is a web app for translating web novels chapter by chapter. As you
translate, it builds a per-novel **glossary** of recurring terms — character and
place names, factions, titles, and the like — and feeds them back into future
translations so names and terminology stay consistent across the whole novel.

It's split into two parts:

- **[`backend/`](backend/README.md)** — FastAPI server: novels, chapters,
  glossary, and the extraction + translation pipeline.
- **[`frontend/`](frontend/README.md)** — Next.js web UI: library, chapter
  upload/reading, and glossary management.

See each directory's README for setup, configuration, and details.

## How it works

### First chapter

1. You create a novel and upload a chapter to it.
2. On upload, the backend extracts readable text (if you uploaded an HTML file), or takes the raw source text that you pasted in.
3. An AI agent extracts key terms from the chapter. Think things like character or place names that should remain consistent for the whole novel.
4. These key terms, and their 'canonical translations', are stored in the glossary (a database).
5. Another AI agent translates the chapter with these key terms (and their canonical translations) as context.
6. Your chapter is translated!

### Subsequent chapters

1. You upload a chapter to an existing novel, and the source text is extracted (as in #2 above).
2. We scan the chapter for mentions of existing glossary terms. (This is a deterministic process.)
3. Steps 3-6 from above are the same.

Note: You can manage the glossary by hand at any time; add, edit, or remove entries to steer future translations.

## Stack

| Layer | Tech |
| --- | --- |
| Backend | FastAPI, SQLModel, SQLite, [`uv`](https://docs.astral.sh/uv/) |
| Translation | LangChain |
| Extraction | trafilatura |
| Frontend | Next.js 16, React 19, TanStack Query, axios |
| UI | shadcn/ui (Base UI), Tailwind CSS, lucide-react |
| Dev runner | [`mprocs`](https://github.com/pvolok/mprocs) |

## Running it

With [`mprocs`](https://github.com/pvolok/mprocs) installed, run both the backend
and frontend together from the repo root:

```bash
mprocs
```

Then open **http://localhost:3000**. To run either side on its own, or to
configure environment variables, see the per-directory READMEs linked above.
</content>
