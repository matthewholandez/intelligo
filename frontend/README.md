# Intelligo — Frontend

The web UI for Intelligo: browse your novel library, upload chapters, read
translations, and manage each novel's glossary. Built with the Next.js App
Router and talks to the [backend](../backend/README.md) over a small REST API.

## Stack

- **Next.js 16** (App Router) + **React 19**
- **TanStack Query** for server state (queries, mutations, cache invalidation)
- **axios** HTTP client
- **shadcn/ui** components on **Base UI**, styled with **Tailwind CSS**
- **lucide-react** icons and **sonner** toasts

> **Note:** This is a current Next.js / React release with breaking changes from
> older versions. See `AGENTS.md` — consult the bundled docs in
> `node_modules/next/dist/docs/` before relying on training-data conventions.

## Setup

```bash
npm install
npm run dev      # http://localhost:3000
```

Other scripts: `npm run build`, `npm run start`, `npm run lint`.

### Talking to the backend

The app calls the backend through `/api/*`, which is rewritten to the FastAPI
server in `next.config.ts`:

```ts
// /api/:path*  ->  http://127.0.0.1:8000/:path*
```

Start the backend first (see [`../backend/README.md`](../backend/README.md)), or
run both together from the repo root with `mprocs`.

## Project layout

```
src/
  app/
    layout.tsx                                  # root layout + providers
    providers.tsx                               # TanStack Query client
    page.tsx                                    # novel library
    novels/[id]/page.tsx                        # novel dashboard (tabs)
    novels/[id]/ChaptersTab.tsx                 # chapter list + upload
    novels/[id]/GlossaryTab.tsx                 # inline glossary editing + search
    novels/[id]/chapters/[chap_id]/page.tsx     # single chapter reader
  components/
    AppShell.tsx, ConfirmDialog.tsx,            # shared layout & dialogs
    EmptyState.tsx, ErrorState.tsx,
    MarkdownView.tsx, UploadChapterDialog.tsx
    ui/                                         # shadcn/ui primitives
  lib/
    api.ts                                      # axios client (one fn per endpoint)
    hooks.ts                                    # TanStack Query hooks wrapping the API
    queryKeys.ts                                # centralized query-key factory
    glossary-highlight.ts                       # highlights glossary terms in text
    utils.ts                                    # cn(), error helpers
  types/index.ts                                # shared TypeScript types (mirror backend schemas)
```

## Data flow

- **`lib/api.ts`** has one function per backend endpoint (e.g. `listNovels`,
  `uploadChapter`, `updateGlossaryEntry`).
- **`lib/hooks.ts`** wraps those in TanStack Query hooks (`useNovels`,
  `useChapters`, `useUploadChapter`, …). Mutations invalidate the relevant
  query keys on success and surface errors via `sonner` toasts; `409` conflicts
  (duplicate glossary terms) are handled inline rather than toasted.
- **`lib/queryKeys.ts`** is the single source of truth for cache keys.

Components consume the hooks rather than calling axios directly.
