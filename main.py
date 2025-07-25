from intelligo.scraper import scrape
from intelligo.translator import Translator
from pathlib import Path
from dotenv import load_dotenv
import os

folder = Path(__file__).parent / 'folder'

output_folder = Path(__file__).parent / 'output'
output_folder.mkdir(parents=True, exist_ok=True)

load_dotenv(Path(__file__).parent / '.env')
key = os.getenv('GEMINI_API_KEY')

for item in folder.glob('*.html'):
    print(f"Processing file: {item.name}")

    scraped_chapter = scrape(item)

    translator = Translator(gemini_api_key=key)

    translated_chapter = translator.translate(
        raw_chapter=scraped_chapter,
    )

    filepath = output_folder / item.name.replace(".html", ".md")

    with open(filepath, 'w', encoding='utf-8') as f:
        if translated_chapter.chapter_number and translated_chapter.chapter_title:
            f.write(f'# Chapter {translated_chapter.chapter_number}: {translated_chapter.chapter_title}\n\n')
        elif translated_chapter.chapter_number:
            f.write(f'# Chapter {translated_chapter.chapter_number}\n\n')
        f.write(translated_chapter.translated_text)

    print(f"Translated chapter saved to: {filepath}")