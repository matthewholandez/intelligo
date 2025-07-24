from trafilatura.metadata import Document


class BookTokiScraper:
    """
    Scraper for novels of booktoki468.com.
    """

    def __init__(self, metadata: Document) -> None:
        self.metadata = metadata
        return None
    

    def get_chapter_number(self) -> int | None:
        """
        Extract the chapter number from the metadata.
        """
        title = self.metadata.title
        if '화' in title:
            try:
                return int((title.split('화')[0].strip()).split(' ')[-1])
            except ValueError:
                return None
        return None
    
    
    def get_novel_title(self) -> str | None:
        """
        Extract the novel title from the metadata.
        """
        if self.metadata.title:
            return self.metadata.title.split('화')[0].strip()
        return None