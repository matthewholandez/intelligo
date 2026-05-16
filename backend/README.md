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

## Schemas

`NovelPublic`:
- `id` (int)
- `name` (str)
- `updated_on` (datetime)
