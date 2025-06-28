import yaml
from pathlib import Path
from intelligo.exceptions import ConfigNotLoadedError, ScraperError
from pydantic import BaseModel
from bs4 import BeautifulSoup
from google import genai
import re
import os

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
    chapter_title: str | None = None

class GeminiChapterOutput(BaseModel):
    """
    Represents the output format for the translated chapter.
    """
    chapter_title: str | None = None
    content: str

class Intelligo:
    """
    Translates Asian web novels into English and formats 
    them into a readable format.

    Arguments:
    - input_file: Path to the input file containing the novel text.
    - context_chapters: Number of previous chapters to include as context (default: 3)
    - output_dir: Directory containing previously translated chapters for context
    """
    def __init__(self, input_file: Path, context_chapters: int = 3, output_dir: Path = None) -> None:
        if not isinstance(input_file, Path):
            raise ValueError("Input file must be a Path object")
        if not input_file.suffix.lower() == '.html':
            raise ValueError("Input file must be an HTML file")
        if not input_file.exists():
            raise FileNotFoundError(f"Input file '{input_file}' not found")
        
    def __init__(self, input_file: Path, context_chapters: int = None, output_dir: Path = None) -> None:
        if not isinstance(input_file, Path):
            raise ValueError("Input file must be a Path object")
        if not input_file.suffix.lower() == '.html':
            raise ValueError("Input file must be an HTML file")
        if not input_file.exists():
            raise FileNotFoundError(f"Input file '{input_file}' not found")
        
        self.input_file = input_file
        
        if not CONFIG or not CONFIG["css_selectors"] or not CONFIG["prompt"]:
            raise ConfigNotLoadedError(
                "Configuration file not loaded or missing required keys."
            )
        
        # Set context chapters from parameter, config, or default
        if context_chapters is not None:
            self.context_chapters = max(0, context_chapters)
        elif CONFIG.get("context", {}).get("previous_chapters") is not None:
            self.context_chapters = max(0, CONFIG["context"]["previous_chapters"])
        else:
            self.context_chapters = 3  # Default value
            
        self.output_dir = output_dir or Path("output")
        self.css_selectors = CONFIG["css_selectors"]
        self.prompt_file = Path(__file__).resolve().parent / CONFIG["prompt"]

        self.soup = self._load_html()
        self.prompt = self._load_prompt()
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        
        return None
    
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
            novel_title = novel_title,
            content = formatted_novel_content,
            number = chapter_number
        )

        return scraped_chapter
    
    def translate_chapter(self) -> TranslatedChapter:
        """
        Scrapes, translates, and formats a chapter of a novel.
        """
        raw_chapter = self.scrape_chapter()
        
        # Get context from previous chapters
        context = self._get_previous_chapters_context(raw_chapter.novel_title, raw_chapter.number)

        raw_chapter_lines = len(raw_chapter.content.split("\n"))
        attempts = 0
        while attempts < 7:
            attempts += 1
            
            # Build the content list for Gemini
            content_list = [self.prompt]
            
            # Add context if available
            if context:
                content_list.append(context)
            
            # Add the novel information and content to translate
            content_list.extend([
                f"For your information, the novel title is {raw_chapter.novel_title}.",
                f"The content you will translate is:\n\n{raw_chapter.content}"
            ])
            
            translated_content = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=content_list,
                config = {
                    "temperature": 0.3,
                    "response_mime_type": "application/json",
                    "response_schema": GeminiChapterOutput,
                    "thinking_config": { "thinking_budget": 1000 }
                }
            )
            print(f"Attempt {attempts}: Translation completed")
            translated_lines = len(translated_content.parsed.content.split("\n"))
            print(f"Original lines: {raw_chapter_lines}, Translated lines: {translated_lines}")
            
            # Check if translation is complete enough (75% of original lines)
            if translated_lines >= int(raw_chapter_lines * 0.75):
                print(f"Translation successful on attempt {attempts}")
                break
            else:
                print(f"Translation incomplete on attempt {attempts}, retrying...")
                
        if attempts == 7:
            raise ScraperError("Failed to translate chapter after 7 attempts.")

        formatted_content = self._format_translated_chapter_content(translated_content.parsed.content, raw_chapter.number, translated_content.parsed.chapter_title)

        return TranslatedChapter(
            novel_title=raw_chapter.novel_title,
            content=formatted_content,
            number=raw_chapter.number,
            chapter_title=translated_content.parsed.chapter_title
        )
    
    def _format_translated_chapter_content(self, content: str, number: int, title: str | None) -> str:
        """
        Formats the translated chapter content.
        """
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        formatted_content = "\n\n".join(lines)
        _formatted_content = f"# Chapter {number}. {title}\n\n" + formatted_content if title else f"# Chapter {number}\n\n" + formatted_content
        return _formatted_content

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
    
    def _get_previous_chapters_context(self, novel_title: str, current_chapter: int) -> str:
        """
        Loads previously translated chapters to provide context for translation consistency.
        
        Args:
            novel_title: The title of the novel
            current_chapter: The current chapter number being translated
            
        Returns:
            A formatted string containing the previous chapters for context
        """
        if self.context_chapters == 0:
            return ""
        
        # Create safe directory name by removing/replacing problematic characters
        # First remove common problematic characters, then replace with underscores
        safe_novel_title = re.sub(r'[<>:"/\\|?*]', '_', novel_title)
        safe_novel_title = re.sub(r'[^\w\s-]', '_', safe_novel_title)  # Keep only word chars, spaces, hyphens
        safe_novel_title = safe_novel_title.strip()
        
        novel_dir = self.output_dir / safe_novel_title
        
        if not novel_dir.exists():
            return ""
        
        previous_chapters = []
        context_text = ""
        
        # Get the range of chapters to include as context
        start_chapter = max(1, current_chapter - self.context_chapters)
        
        for chapter_num in range(start_chapter, current_chapter):
            chapter_file = novel_dir / f"ch-{chapter_num}.md"
            if chapter_file.exists():
                try:
                    with open(chapter_file, "r", encoding="utf-8") as file:
                        chapter_content = file.read()
                        previous_chapters.append(f"=== CHAPTER {chapter_num} ===\n{chapter_content}\n")
                except Exception:
                    continue  # Skip if file can't be read
        
        if previous_chapters:
            context_text = f"""
PREVIOUS CHAPTERS FOR CONTEXT (maintain consistency with these translations):
{''.join(previous_chapters)}
=== END OF CONTEXT ===

Please maintain consistency with character names, gender references, honorifics, and terminology used in the above context.
"""
        
        return context_text