import tomllib
import json
from urllib import request, error
from pathlib import Path
from intelligo.types import IntelligoConfig, IntelligoConfigOpenRouter, ChapterResponse, GlossaryUpdate, ScrapedChapter, \
    TranslatedChapter, IntelligoConfigConstants
from intelligo.prompts.korean import get_korean_prompt

class Translator:
    """
    Uses OpenRouter API to translate web novel chapters to English.
    """
    def __init__(self, openrouter_api_key: str, glossary_path: Path | None = None) -> None:
        self.openrouter_api_key = openrouter_api_key
        self.openrouter_base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.glossary_path = glossary_path
        with open(Path(__file__).parent / "config.toml", "rb") as f:
            config = tomllib.load(f)
        self.config = IntelligoConfig(
            openrouter=IntelligoConfigOpenRouter(model=config['openrouter']['model'],
                                                 temperature=config['openrouter']['temperature']),
            constants=IntelligoConfigConstants(max_attempts=config['constants']['max_attempts'],
                                               acceptable_line_count_ratio=config['constants']['acceptable_line_count_ratio'],),
        )
        self.glossary = self._load_glossary()


    def _load_glossary(self) -> dict[str, str]:
        if self.glossary_path is None or not self.glossary_path.exists():
            return {}

        try:
            with open(self.glossary_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

        if not isinstance(data, dict):
            return {}

        glossary: dict[str, str] = {}
        for source_term, preferred_translation in data.items():
            if isinstance(source_term, str) and isinstance(preferred_translation, str):
                source = source_term.strip()
                target = preferred_translation.strip()
                if source and target:
                    glossary[source] = target
        return glossary


    def _save_glossary(self) -> None:
        if self.glossary_path is None:
            return

        self.glossary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.glossary_path, "w", encoding="utf-8") as f:
            json.dump(self.glossary, f, indent=2, ensure_ascii=False)


    def _build_glossary_instructions(self) -> str | None:
        if not self.glossary:
            return None

        glossary_lines = [
            f"- {source_term} => {preferred_translation}"
            for source_term, preferred_translation in sorted(self.glossary.items(), key=lambda x: x[0].casefold())
        ]
        return "\n".join(glossary_lines)


    def _merge_glossary_updates(self, updates: list[GlossaryUpdate]) -> None:
        glossary_changed = False
        for update in updates:
            source_term = update.source_term.strip()
            preferred_translation = update.preferred_translation.strip()

            if not source_term or not preferred_translation:
                continue

            if source_term not in self.glossary:
                self.glossary[source_term] = preferred_translation
                glossary_changed = True

        if glossary_changed:
            self._save_glossary()


    def translate(self, 
                  raw_chapter: ScrapedChapter,
                  additional_instructions: str | None = None) -> TranslatedChapter:
        """
        Translate a scraped chapter into English.
        """

        # Get prompt
        prompt = get_korean_prompt(
            raw_chapter.raw_text,
            additional_instructions=additional_instructions,
            glossary_instructions=self._build_glossary_instructions(),
        )

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
                self._merge_glossary_updates(parsed_response.glossary_updates)
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
