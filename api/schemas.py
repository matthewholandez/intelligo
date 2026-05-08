from pydantic import BaseModel


class Series(BaseModel):
    id: str
    name: str
    created_at: str


class SeriesPostRequest(BaseModel):
    name: str


class SeriesPostResponse(BaseModel):
    id: str
    name: str


class TranslatedChapter(BaseModel):
    name: str | None
    body: str


class GlossaryEntry(BaseModel):
    term: str
    translation: str


class GlossaryEntryList(BaseModel):
    items: list[GlossaryEntry]


class TranslateResponse(BaseModel):
    ok: bool