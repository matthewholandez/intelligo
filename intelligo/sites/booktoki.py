from trafilatura.metadata import Document
from intelligo.types import ScrapedChapterMetadata


class BookTokiScraper:
    """
    Scraper for novels of booktoki468.com.
    """

    def __init__(self, metadata: Document) -> None:
        self.metadata = metadata
        return None
    

    def get_chapter_number(self) -> int | None:
        title = self.metadata.title
        if '화' in title:
            try:
                return int((title.split('화')[0].strip()).split(' ')[-1])
            except ValueError:
                return None
        return None
    
    
    def get_novel_title(self) -> str | None:
        title = self.metadata.title

        # Find the pattern of number + '화' to identify where the chapter number starts
        import re
        match = re.search(r'\s+\d+화', title)
        if match:
            # Extract everything before the chapter number
            novel_title = title[:match.start()].strip()
            return novel_title

        # If no chapter pattern found, fall back to splitting on '>'
        return title.split('>')[0].strip()
