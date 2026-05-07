# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Intelligo is a CLI tool that translates Asian web novel chapters (HTML) into English Markdown, using LLMs via OpenRouter. Korean is the only fully wired language at the moment; a Chinese prompt exists but isn't reachable from `scrape()` yet.

The repo's current `ui-rewrite` branch also contains design artifacts for an eventual web frontend — `DESIGN_SPEC.md`, `mockup.html`, `branding/` — but no frontend code yet. The shipping product is still the CLI.

## Commands

```bash
# setup (one-time)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mv .env.example .env   # then add OPENROUTER_API_KEY

# run
python main.py --help
python main.py                                   # defaults: input/ -> output/, glossary at output/term_glossary.json
python main.py --input-dir <dir> --output-dir <dir> --glossary-file <path>
```

There is no test suite, lint config, or build step. Don't invent commands for them.

## Architecture

The pipeline is three stages, orchestrated by `main.py`:

1. **`scraper.scrape(html_file)`** → `ScrapedChapter` (raw text + metadata).
   Trafilatura does generic extraction; site-specific dispatch in `get_detailed_metadata()` and `process_raw_text()` matches on URL hostname. Only `booktoki468.com` has a custom path right now (`intelligo/sites/booktoki.py`).
2. **`Translator.translate(chapter, additional_instructions)`** → `TranslatedChapter`.
   Builds a Korean translation prompt, POSTs to OpenRouter, retries up to `max_attempts` until the response passes a line-count sanity check (`acceptable_line_count_ratio`, default 0.75 of source non-empty lines). On success, merges any `glossary_updates` from the model into the persisted glossary.
3. **`main.py`** writes the result as Markdown.

Three cross-cutting behaviors are load-bearing and easy to miss:

- **Self-building glossary.** Each translation can return `glossary_updates`; new entries are appended to `term_glossary.json` (never overwriting existing keys, to keep canonical translations stable). On the next chapter, all current entries are injected into the prompt as `source => preferred_translation` lines. This is what keeps proper-noun translations consistent across a long novel.
- **Previous-chapter context.** `get_previous_chapters_context()` in `main.py` reads up to the 3 most-recently-translated `.md` files in the output directory (sorted lexicographically) and passes them to the translator wrapped in `<previous_chapter_for_context>` tags. Naming input files so that lexicographic sort matches reading order matters.
- **Resume-by-skipping.** `main.py` skips any input HTML whose corresponding `.md` already exists in the output directory. To re-translate a chapter, delete its output file. There is no `--force` flag.

## Adding a new source site

1. New class in `intelligo/sites/<site>.py` exposing at minimum `get_novel_title()` and `get_chapter_number()`. Mirror `BookTokiScraper`.
2. Add a `case "<hostname>":` arm to **both** `get_detailed_metadata()` and `process_raw_text()` in `intelligo/scraper.py` — the hostname must match what `urlparse(metadata.url).hostname` returns (e.g., `booktoki468.com`, including subdomain).

## Adding a new source language

Prompts live in `intelligo/prompts/<lang>.py` as a single `get_<lang>_prompt(source_text, additional_instructions, glossary_instructions)` function. `translator.py` currently hardcodes `get_korean_prompt`; switching languages today means editing that import. There is no language-detection or routing layer yet.

## Configuration surfaces

- `intelligo/config.toml` — committed. Model, temperature, retry constants. Change the model here, not in code.
- `.env` — gitignored. `OPENROUTER_API_KEY` only.
- CLI flags — input dir, output dir, glossary path. No flag for model or language.

## Conventions worth knowing

- Pydantic models in `intelligo/types.py` are the contract between stages — `ScrapedChapter`, `TranslatedChapter`, `ChapterResponse` (the LLM's expected JSON shape), `GlossaryUpdate`. Changing any of these ripples through the pipeline.
- The model is asked for `response_format: {"type": "json_object"}`, but the code still defensively strips ```` ``` ```` fences before `model_validate_json` because not every OpenRouter model honors it.
- Glossary writes use `ensure_ascii=False` — the file is UTF-8 and contains Hangul. Don't change that.
