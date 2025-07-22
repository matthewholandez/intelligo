from src.intelligo.prompts.korean import get_korean_prompt
from src.intelligo.types import ScrapedChapter, TranslatedChapter, IntelligoConfig, GeminiConfig, GeminiChapterResponse
from google import genai
from google.genai import types
from pydantic import BaseModel
from pathlib import Path
from os import getenv
import tomllib


class Intelligo:
    """
    Intelligo: translate your favourite Asian web novels to English.
    """

    def __init__(self) -> None:
        self.gemini_client = genai.Client(api_key=getenv("GEMINI_API_KEY"))
        
        with open(Path(__file__).parent / "config.toml", "rb") as f:
            config = tomllib.load(f)
        self.config: IntelligoConfig = config


    def scrape(self, source_file: Path) -> ScrapedChapter:
        """
        Scrape a source file to extract chapter information.
        """
        # Placeholder for actual scraping logic
        # This should return a ScrapedChapter object with title, number, and text
        return ScrapedChapter(title="Sample Chapter", number=1, text="This is a sample chapter text.")


    def translate(self, source_file: Path, additional_instructions: str | None = None) -> TranslatedChapter:
        """
        Translate a scraped chapter into English.
        """
        # Scrape the source file
        scraped_chapter = self.scrape(source_file)

        # Get prompt
        raw_novel_title = scraped_chapter.novel_title
        prompt = get_korean_prompt(scraped_chapter.raw_text, additional_instructions=additional_instructions)

        # Translate the scraped chapter using Gemini
        response = self.gemini_client.models.generate_content(
            model=self.config.gemini.model,
            contents=[prompt, f"<raw_novel_title>{raw_novel_title}</raw_novel_title>"],
            config=types.GenerateContentConfig(
                temperature=self.config.gemini.temperature,
                thinking_budget=types.ThinkingConfig(thinking_budget=self.config.gemini.thinking_budget),
                response_mime_type="application/json",
                response_schema=GeminiChapterResponse
            )
        )

        return TranslatedChapter(
            novel_title=raw_novel_title,
            chapter_title=response.parsed.get("chapter_title", ""),
            chapter_number=scraped_chapter.chapter_number,
            translated_text=response.parsed.get("translated_text")
        )


