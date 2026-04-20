import tomllib
import json
from urllib import request, error
from pathlib import Path
from intelligo.types import IntelligoConfig, IntelligoConfigOpenRouter, ChapterResponse, ScrapedChapter, \
    TranslatedChapter, IntelligoConfigConstants
from intelligo.prompts.korean import get_korean_prompt

class Translator:
    """
    Uses OpenRouter API to translate web novel chapters to English.
    """
    def __init__(self, openrouter_api_key: str) -> None:
        self.openrouter_api_key = openrouter_api_key
        self.openrouter_base_url = "https://openrouter.ai/api/v1/chat/completions"
        with open(Path(__file__).parent / "config.toml", "rb") as f:
            config = tomllib.load(f)
        self.config = IntelligoConfig(
            openrouter=IntelligoConfigOpenRouter(model=config['openrouter']['model'],
                                                 temperature=config['openrouter']['temperature']),
            constants=IntelligoConfigConstants(max_attempts=config['constants']['max_attempts'],
                                               acceptable_line_count_ratio=config['constants']['acceptable_line_count_ratio'],),
        )


    def translate(self, 
                  raw_chapter: ScrapedChapter,
                  additional_instructions: str | None = None) -> TranslatedChapter:
        """
        Translate a scraped chapter into English.
        """

        # Get prompt
        prompt = get_korean_prompt(raw_chapter.raw_text, additional_instructions=additional_instructions)

        raw_text_length = len([x for x in raw_chapter.raw_text.splitlines() if x != ""])

        parsed_response: ChapterResponse

        attempts = 0
        while attempts < self.config.constants.max_attempts:
            payload = {
                "model": self.config.openrouter.model,
                "temperature": self.config.openrouter.temperature,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"{prompt}\n\n"
                            f"<raw_novel_title>{raw_chapter.metadata.novel_title}</raw_novel_title>"
                        ),
                    }
                ],
            }

            req = request.Request(
                self.openrouter_base_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )

            try:
                with request.urlopen(req) as response:
                    response_data = json.loads(response.read().decode("utf-8"))
            except (error.HTTPError, error.URLError, json.JSONDecodeError):
                attempts += 1
                continue

            choices = response_data.get("choices", [])
            if not choices:
                attempts += 1
                continue

            content = choices[0].get("message", {}).get("content", "")
            if not isinstance(content, str) or not content.strip():
                attempts += 1
                continue

            cleaned_content = content.strip()
            if cleaned_content.startswith("```"):
                cleaned_content = cleaned_content.strip("`")
                cleaned_content = cleaned_content.replace("json", "", 1).strip()

            try:
                parsed_response = ChapterResponse.model_validate_json(cleaned_content)
            except Exception:
                attempts += 1
                continue
            
            translated_text_length = len([x for x in parsed_response.translated_text.splitlines() if x != ""])
            if translated_text_length > (raw_text_length * self.config.constants.acceptable_line_count_ratio):
                break
            attempts += 1
        else:
            # This block executes if the while loop completes without a break
            raise Exception("Failed to get a valid translation after maximum attempts.")

        return TranslatedChapter(
            novel_title=raw_chapter.metadata.novel_title,
            chapter_title=parsed_response.chapter_title,
            chapter_number=raw_chapter.metadata.chapter_number,
            translated_text=parsed_response.translated_text
        )
