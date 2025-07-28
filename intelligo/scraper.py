from pathlib import Path
from intelligo.types import ScrapedChapter, ScrapedChapterMetadata
from intelligo.exceptions import InvalidSourceFileError
from trafilatura import extract, extract_metadata
from trafilatura.metadata import Document
from urllib.parse import urlparse
from intelligo.sites.booktoki import BookTokiScraper


def scrape(source_file: Path) -> ScrapedChapter:
    """
    Scrape a chapter from the source HTML file.
    """

    if not source_file.glob("*.html"):
        raise InvalidSourceFileError("The source file is not a valid HTML file.")

    with open(source_file, "r") as f:
        html_content: str = f.read()

    metadata = extract_metadata(html_content)
    if not metadata.url and metadata.title:
        raise InvalidSourceFileError("The source file could not be read.")
    detailed_metadata = get_detailed_metadata(metadata)

    raw_text = extract(html_content)
    text = process_raw_text(metadata=metadata, raw_text=raw_text)

    return ScrapedChapter(
        raw_text=text,
        metadata=detailed_metadata
    )


def get_detailed_metadata(metadata: Document) -> ScrapedChapterMetadata:
    """
    Try to extract the novel title and chapter number.
    Works best if the site is known.
    """

    parsed_url = urlparse(metadata.url)
    hostname = parsed_url.hostname

    match hostname:
        case "booktoki468.com":
            booktoki = BookTokiScraper(metadata)
            return ScrapedChapterMetadata(
                novel_title=booktoki.get_novel_title(),
                chapter_number=booktoki.get_chapter_number(),
            )
        case _:
            return ScrapedChapterMetadata(
                novel_title=metadata.title,
                chapter_number=None,
            )


def process_raw_text(metadata: Document, raw_text: str) -> str:
    """
    If the site is known, apply post-processing to the raw text.
    This is useful for sites that have a specific format or structure.
    """
    parsed_url = urlparse(metadata.url)
    hostname = parsed_url.hostname

    match hostname:
        case "booktoki468.com":
            return '\n'.join(raw_text.split('\n')[:-1])
        case _:
            return raw_text


class Scraper:
    """
    Scrape features of a web novel chapter from
    a source HTML file.
    """

    def __init__(self) -> None:
        pass
