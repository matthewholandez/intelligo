import yaml
from pathlib import Path
from intelligo.exceptions import ConfigNotLoadedError, ScraperError
from intelligo.types import RawChapter, TranslatedChapter, GeminiChapterOutput
from intelligo.scraper import WebNovelScraper
from google import genai
import os

class Intelligo:
    """
    Translates Asian web novels into English and formats 
    them into a readable format.

    Arguments:
    - input_file: Path to the input file containing the novel text.
    - context_chapters: Number of previous chapters to include as context (default: 3)
    - output_dir: Directory containing previously translated chapters for context
    """ 
    def __init__(self, input_file: Path, additional_instructions: str | None = None) -> None:
        # Verify all arguments are valid.
        if not isinstance(input_file, Path):
            raise ValueError("Input file must be a Path object")
        if not input_file.suffix.lower() == '.html':
            raise ValueError("Input file must be an HTML file")
        if not input_file.exists():
            raise FileNotFoundError(f"Input file '{input_file}' not found")
        self.input_file = input_file

        # Verify config.yaml is valid.
        try:
            with open(Path(__file__).resolve().parent / "config.yaml", "r", encoding="utf-8") as file:
                CONFIG = yaml.safe_load(file)
        except FileNotFoundError:
            raise ConfigNotLoadedError("Configuration file 'config.yaml' not found.")
        
        if not CONFIG or not CONFIG["css_selectors"] or not CONFIG["prompt"] or not CONFIG["preferences"]:
            raise ConfigNotLoadedError(
                "Configuration file missing required keys."
            )
        
        # Load config from config.yaml.
        self.css_selectors = CONFIG["css_selectors"]
        self.prompt_file = Path(__file__).resolve().parent / CONFIG["prompt"]
        self.prompt = self._load_prompt()
        self.additional_instructions = additional_instructions
        self.preferences = CONFIG["preferences"]

        # Initialize scraper and Gemini client.
        self.scraper = WebNovelScraper(input_file, self.css_selectors)
        self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        return None
    

    def scrape_chapter(self) -> RawChapter:
        """
        Extracts the novel title and content from the web page using the scraper.
        """
        return self.scraper.scrape_chapter()


    def translate_chapter(self) -> TranslatedChapter:
        """
        Scrapes, translates, and formats a chapter of a novel.
        """
        raw_chapter = self.scrape_chapter()

        raw_chapter_lines = len(raw_chapter.content.split("\n")) # Count lines to verify translation completeness
        attempts = 0
        while attempts < self.preferences.get("max_translation_attempts", 7):
            attempts += 1
            
            # Build the content list for Gemini
            content_list = [self.prompt,
                            f"For your information, the novel title in Korean is {raw_chapter.novel_title}. Do not use this as the chapter title you output."]
            
            # Add context from previous chapters if available.
            if self.additional_instructions:
                content_list.append(f"The following additional instructions should also be followed:\n\n{self.additional_instructions}")

            # Finally, append the raw chapter content.
            content_list.append(f"Here is the chapter you will translate into English:\n\n{raw_chapter.content}")
            
            try:
                translated_content = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=content_list,
                    config={
                        "temperature": 0.3,
                        "response_mime_type": "application/json",
                        "response_schema": GeminiChapterOutput,
                        "thinking_config": { "thinking_budget": 1000 }
                    }
                )
            except Exception as e:
                print(f"Error during translation attempt {attempts}: {e}")
                if attempts == 7:
                    raise ScraperError("Failed to translate chapter after 7 attempts.")
                continue
            print(f"Attempt {attempts}: Translation completed")
            translated_lines = len(translated_content.parsed.content.split("\n"))
            print(f"Original lines: {raw_chapter_lines}, Translated lines: {translated_lines}")
            
            # Check if translation is complete enough (75% of original lines)
            if translated_lines >= int(raw_chapter_lines * self.preferences.get("translation_completeness_threshold", 0.75)):
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
        Formats the translated chapter content by ensuring lines are always double spaced.
        """
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        formatted_content = "\n\n".join(lines)
        _formatted_content = f"# Chapter {number}. {title}\n\n" + formatted_content if title else f"# Chapter {number}\n\n" + formatted_content
        return _formatted_content


    def _load_prompt(self) -> str:
        """
        Loads the prompt from the prompt file.
        """
        if not self.prompt_file.is_file():
            raise FileNotFoundError(f"Prompt file {self.prompt_file} not found.")
        with open(self.prompt_file, "r", encoding="utf-8") as file:
            return file.read()