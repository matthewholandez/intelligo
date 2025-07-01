from bs4 import BeautifulSoup
from pathlib import Path
import re
from intelligo.exceptions import ScraperError
from intelligo.types import RawChapter


class WebNovelScraper:
    """
    Handles web scraping functionality for web novel content.
    """
    
    def __init__(self, input_file: Path, css_selectors: dict):
        """
        Initialize the scraper with an HTML file and CSS selectors.
        
        Args:
            input_file: Path to the HTML file to scrape
            css_selectors: Dictionary containing CSS selectors for scraping
        """
        self.input_file = input_file
        self.css_selectors = css_selectors
        self.soup = self._load_html()


    def scrape_chapter(self) -> RawChapter:
        """
        Extracts the novel title and content from the web page.
        """
        novel_content = self.soup.select_one(self.css_selectors["chapter_content"])
        if novel_content and len(novel_content.contents) >= 4:
            content_container = novel_content.contents[3]
            
            # First try to find paragraph tags
            paragraphs = content_container.find_all("p")
            if paragraphs:
                formatted_novel_content = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            else:
                # If no paragraphs found, try div tags
                divs = content_container.find_all("div")
                if divs:
                    # Filter out divs that only contain <br> tags or are empty
                    text_divs = []
                    for div in divs:
                        text_content = div.get_text(strip=True)
                        if text_content and text_content != "":
                            text_divs.append(text_content)
                    formatted_novel_content = "\n\n".join(text_divs)
                else:
                    raise ScraperError("No paragraph or div content found.")
            
            if not formatted_novel_content:
                raise ScraperError("No readable content found.")
        else:
            raise ScraperError("Chapter content not found.")

        raw_title = self.soup.select_one('.bottom-wrapper > div:nth-child(2) > div:nth-child(1)').contents[0].strip()
        if not raw_title:
            raise ScraperError("Novel title not found.")
        
        chapter_match = re.search(r'(\d+)화', raw_title)
        if chapter_match:
            chapter_number = int(chapter_match.group(1))
        else:
            chapter_number = 1
        
        novel_title = re.sub(r'-?\d+화$', '', raw_title).strip() 

        scraped_chapter = RawChapter(
            novel_title=novel_title,
            content=formatted_novel_content,
            number=chapter_number
        )

        return scraped_chapter
    

    def _load_html(self) -> BeautifulSoup:
        """
        Loads the HTML content from the input file.
        """
        with open(self.input_file, "r", encoding="utf-8") as file:
            html_content = file.read()
        return BeautifulSoup(html_content, "html.parser")
