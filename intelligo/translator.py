import tomllib
from pathlib import Path
from intelligo.types import IntelligoConfig, GeminiConfig, GeminiChapterResponse, ScrapedChapter, TranslatedChapter
from intelligo.prompts.korean import get_korean_prompt
from google import genai
from google.genai import types

class Translator:
    """
    Uses Google's Gemini API to translate web novel chapters to English.
    """
    def __init__(self, gemini_api_key: str) -> None:
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        with open(Path(__file__).parent / "config.toml", "rb") as f:
            config = tomllib.load(f)
        self.config = IntelligoConfig(
            gemini=GeminiConfig(model=config['gemini']['model'],
                                temperature=config['gemini']['temperature'],
                                thinking_budget=config['gemini']['thinking_budget'],)
        )


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
            contents=[prompt, f"<raw_novel_title>{raw_chapter.metadata.novel_title}</raw_novel_title>"],
            config=types.GenerateContentConfig(
                temperature=self.config.gemini.temperature,
                thinking_config=types.ThinkingConfig(thinking_budget=self.config.gemini.thinking_budget),
                response_mime_type="application/json",
                response_schema=GeminiChapterResponse
            )
        )

        parsed_response: GeminiChapterResponse = response.parsed

        return TranslatedChapter(
            novel_title=raw_chapter.metadata.novel_title,
            chapter_title=parsed_response.chapter_title,
            chapter_number=raw_chapter.metadata.chapter_number,
            translated_text=parsed_response.translated_text
        )



