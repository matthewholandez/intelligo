from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class Series(BaseModel):
    id: str
    name: str
    created_at: str


class SeriesPostRequest(BaseModel):
    name: str


class SeriesPostResponse(BaseModel):
    id: str
    name: str


class Novel(CamelModel):
    slug: str
    name: str
    is_current: bool = False


class NovelList(CamelModel):
    items: list[Novel]


class NovelPostResponse(CamelModel):
    id: str
    slug: str
    name: str


class ChapterRef(CamelModel):
    number: int
    name: str | None = None


class ChapterRefList(CamelModel):
    items: list[ChapterRef]


class GlossaryEntry(CamelModel):
    term: str
    translation: str
    tag: str | None = None


class GlossaryEntryList(CamelModel):
    items: list[GlossaryEntry]


class TermRow(CamelModel):
    source: str
    preferred: str
    tag: str | None = None
    chapter: int


class TermRowList(CamelModel):
    items: list[TermRow]


class TranslatedChapter(BaseModel):
    name: str | None
    body: str


class Chapter(CamelModel):
    number: int
    name: str | None = None
    body: str
    prev: ChapterRef | None = None
    next: ChapterRef | None = None
    glossary: list[GlossaryEntry] = []


class Bookmark(CamelModel):
    novel_slug: str
    novel_name: str
    chapter: int
    title: str
    preview: str
    chapters_last_24h: int = 0


class RecentChapter(CamelModel):
    novel: str
    novel_slug: str
    title: str | None = None
    preview: str
    chapter: int


class RecentChapterList(CamelModel):
    items: list[RecentChapter]


class PressItem(CamelModel):
    novel: str
    chapter: int
    status: str
    attempt: int
    attempt_of: int


class PressItemList(CamelModel):
    items: list[PressItem]


class TranslateResponse(BaseModel):
    ok: bool
