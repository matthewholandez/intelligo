import yaml
from pathlib import Path
from intelligo.exceptions import ConfigNotLoadedError, ScraperError
from pydantic import BaseModel
from bs4 import BeautifulSoup
from google import genai
import re

try:
    with open(Path(__file__).resolve().parent / "config.yaml", "r", encoding="utf-8") as file:
        CONFIG = yaml.safe_load(file)
except FileNotFoundError:
    CONFIG = {}

class RawChapter(BaseModel):
    """
    Represents a chapter of a novel in its raw form.
    """
    novel_title: str
    content: str
    number: int

class TranslatedChapter(RawChapter):
    """
    Represents a chapter of a novel after translation.
    """
    chapter_title: str

class Intelligo:
    """
    Translates Asian web novels into English and formats 
    them into a readable format.

    Arguments:
    - input_file: Path to the input file containing the novel text.
    - output_dir: Path to the output directory where the formatted text will be saved."
    """
    def __init__(self, input_file: Path, output_dir: Path) -> None:
        assert (isinstance(input_file, Path) and isinstance(output_dir, Path)), "Input and output files must be Path objects."
        assert input_file.glob("*.html"), "Input file must be an HTML file."
        self.input_file = input_file
        assert output_dir.is_dir(), "Output file must be a directory."
        self.output_dir = output_dir

        if not CONFIG or not CONFIG["constants"]["css_selectors"] or not CONFIG["constants"]["prompt"]:
            raise ConfigNotLoadedError(
                "Configuration file not loaded or missing required keys."
            )
        self.constants = CONFIG["constants"]
        self.css_selectors = self.constants["css_selectors"]
        self.prompt_file = Path(__file__).resolve().parent / self.constants.get("prompt", "prompt.md")

        self.soup = self._load_html()
        self.prompt = self._load_prompt()
        
        return None
    
    def translate_chapter(self) -> TranslatedChapter:
        """
        Scrapes, translates, and formats a chapter of a novel.
        """
        raw_chapter = self._scrape_chapter()

    def _scrape_chapter(self) -> RawChapter:
        """
        Extracts the novel title and content from the web page.
        """
        novel_content = self.soup.select_one(self.css_selectors["chapter_content"])
        if novel_content and len(novel_content.contents) >= 4:
            content_container = novel_content.contents[3]
            paragraphs = content_container.find_all("p") or content_container.find_all("div")
            formatted_novel_content = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text())
        else:
            raise ScraperError("Chapter content not found.")
        
        novel_title = self.soup.select_one('.bottom-wrapper > div:nth-child(2) > div:nth-child(1)').contents[0].strip()
        if not novel_title:
            raise ScraperError("Novel title not found.")
        
        # HERE
        # Extract chapter number from title (number preceding "화")
        chapter_match = re.search(r'(\d+)화', novel_title)
        if chapter_match:
            chapter_number = int(chapter_match.group(1))
        else:
            chapter_number = 1  # Default fallback


        scraped_chapter = RawChapter(
            novel_title = novel_title,
            content = formatted_novel_content,
            number = chapter_number  # Use extracted chapter number
        )
        return scraped_chapter

    def _load_html(self) -> BeautifulSoup:
        """
        Loads the HTML content from the input file.
        """
        with open(self.input_file, "r", encoding="utf-8") as file:
            html_content = file.read()
        return BeautifulSoup(html_content, "html.parser")
    
    def _load_prompt(self) -> str:
        """
        Loads the prompt from the prompt file.
        """
        if not self.prompt_file.is_file():
            raise FileNotFoundError(f"Prompt file {self.prompt_file} not found.")
        with open(self.prompt_file, "r", encoding="utf-8") as file:
            return file.read()