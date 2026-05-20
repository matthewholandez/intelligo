# Intelligo - Backend

Intelligo's backend is a FastAPI server that handles all translation requests.

```bash
uv sync

uv run fastapi dev
```

## Routes

### `GET /novels`

List novels.

Query parameters:
- `offset` (int, default `0`)
- `limit` (int, default `100`, max `100`)

Returns `200`: `list[NovelPublic]`.

### `GET /novels/{novel_id}`

Get a novel by ID.

Returns `200`: `NovelPublic`, or `404` if not found.

### `POST /novels`

Create a novel.

Body (`NovelCreate`):
- `name` (str)

Returns `200`: `NovelPublic`.

### `PATCH /novels/{novel_id}`

Update a novel. Only fields provided in the body are modified.

Body (`NovelUpdate`):
- `name` (str)

Returns `200`: `NovelPublic`, or `404` if not found.

### `DELETE /novels/{novel_id}`

Delete a novel.

Returns `200`: `{ "ok": true }`, or `404` if not found.

### `POST /novels/{novel_id}/chapters`

Upload a chapter. Accepts `multipart/form-data` (file upload).

Form fields:
- `number` (int, required)
- `file` (UploadFile, optional) — `.md` or `.html`, UTF-8, max 5 MB
- `source_text` (str, optional)

Exactly one of `file` or `source_text` must be provided. File contents are stored verbatim in `source_text` (no extraction).

Returns `200`: `ChapterPublic`, `400` on bad input, `404` if the novel is missing, `413` if the file exceeds 5 MB.

### `GET /novels/{novel_id}/chapters`

List chapters for a novel, ordered by `number`.

Returns `200`: `list[ChapterPublic]`, or `404` if the novel is missing.

### `GET /novels/{novel_id}/chapters/{chap_id}`

Get a single chapter.

Returns `200`: `ChapterPublic`, or `404` if not found under that novel.

### `PATCH /novels/{novel_id}/chapters/{chap_id}`

Update a chapter. Only fields provided in the body are modified.

Body (`ChapterUpdate`):
- `number` (int, optional)
- `source_text` (str, optional)
- `translated_text` (str, optional)

Returns `200`: `ChapterPublic`, or `404` if not found.

### `DELETE /novels/{novel_id}/chapters/{chap_id}`

Delete a chapter.

Returns `200`: `{ "ok": true }`, or `404` if not found.

## Schemas

`NovelPublic`:
- `id` (int)
- `name` (str)
- `updated_on` (datetime)

`ChapterPublic`:
- `id` (int)
- `novel_id` (int)
- `number` (int)
- `source_text` (str)
- `translated_text` (str | null)
- `updated_on` (datetime)
