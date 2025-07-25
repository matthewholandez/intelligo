from pathlib import Path
from intelligo.types import ScrapedChapter
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

    text = extract(html_content)

    metadata = extract_metadata(html_content)
    if not metadata.url and metadata.title:
        raise InvalidSourceFileError("The source file could not be read.")

    return ScrapedChapter(
        raw_text=text,
        novel_title="Example Novel",
        chapter_number=1
    )


def get_novel_title_from_known_site(url: str, metadata: Document) -> str | None:
    """
    Try to extract the novel title if the site is known.
    """

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    match hostname:
        case "booktoki468.com":
            return BookTokiScraper(metadata=metadata).get_novel_title()
        case _:
            return None


class Scraper:
    """
    Scrape features of a web novel chapter from
    a source HTML file.
    """

    def __init__(self) -> None:
        pass
