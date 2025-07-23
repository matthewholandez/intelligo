import tomllib
from pathlib import Path
from intelligo.types import IntelligoConfig, TranslatedChapter, GeminiChapterResponse, ScrapedChapter
from intelligo.prompts.korean import get_korean_prompt
from google import genai
from google.genai import types
from os import getenv


class Translator:
    """
    Uses Google's Gemini API to translate web novel chapters to English.
    """
    def __init__(self) -> None:
        self.gemini_client = genai.Client(api_key=getenv("GEMINI_API_KEY"))
        with open(Path(__file__).parent / "config.toml", "rb") as f:
            config: IntelligoConfig = tomllib.load(f)
        self.config = config
        return None
    
    def translate(self, 
                  raw_chapter: ScrapedChapter,
                  additional_instructions: str | None = None) -> TranslatedChapter:
        """
        Translate a scraped chapter into English.
        """

        # Get prompt
        prompt = get_korean_prompt(raw_chapter.raw_text, additional_instructions=additional_instructions)

        # Translate the scraped chapter using Gemini
        response = self.gemini_client.models.generate_content(
            model=self.config.gemini.model,
            contents=[prompt, f"<raw_novel_title>{raw_chapter.novel_title}</raw_novel_title>"],
            config=types.GenerateContentConfig(
                temperature=self.config.gemini.temperature,
                thinking_budget=types.ThinkingConfig(thinking_budget=self.config.gemini.thinking_budget),
                response_mime_type="application/json",
                response_schema=GeminiChapterResponse
            )
        )

        return TranslatedChapter(
            novel_title=raw_chapter.novel_title,
            chapter_title=response.parsed.get("chapter_title", ""),
            chapter_number=raw_chapter.chapter_number,
            translated_text=response.parsed.get("translated_text")
        )



