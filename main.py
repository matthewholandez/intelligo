from intelligo.scraper import scrape
from intelligo.translator import Translator
from pathlib import Path
from dotenv import load_dotenv
import os
import click

load_dotenv(Path(__file__).parent / '.env')
gemini_api_key = os.getenv('GEMINI_API_KEY', '')
translator = Translator(gemini_api_key)

def get_previous_chapters_context(current_file, context_folder, max_chapters=3) -> str | None:
    """
    Get the content of the previous max_chapters files in the context_folder.

    Parameters:
        current_file (Path): The current file being processed
        context_folder (Path): The folder containing previously translated chapters
        max_chapters (int): The maximum number of previous chapters to include in the context

    Returns:
        str | None: A string containing the content of the previous chapters wrapped in <previous_chapter_for_context> tags,
                     or None if no previous chapters are found.
    """
    existing_outputs = sorted(context_folder.glob('*.md'))

    if not existing_outputs:
        return None

    current_output_name = current_file.name.replace(".html", ".md")

    previous_files = []
    for output_file in existing_outputs:
        if output_file.name == current_output_name:
            break
        previous_files.append(output_file)

    # Take the last max_chapters files
    context_files = previous_files[-max_chapters:]

    if not context_files:
        return None

    context_chapters = []
    for file_path in context_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as fi:
                content = fi.read().strip()
                context_chapters.append(f'<previous_chapter_for_context>\n{content}\n</previous_chapter_for_context>')
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            continue

    if not context_chapters:
        return None

    return '\n\n'.join(context_chapters)


@click.command()
@click.option('--input-dir', default='input', help='The directory containing the HTML files to be translated.', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('--output-dir', default='output', help='The directory where the translated Markdown files will be saved.', type=click.Path(file_okay=False, path_type=Path))
def main(input_dir: Path, output_dir: Path):
    """
    A CLI tool to translate HTML chapters into Markdown files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    for item in sorted(input_dir.glob('*.html')):
        print(f"Processing file: {item.name}")

        scraped_chapter = scrape(item)

        previous_translated_chapters = get_previous_chapters_context(item, output_dir)

        translated_chapter = translator.translate(
            raw_chapter=scraped_chapter,
            additional_instructions=previous_translated_chapters,
        )
        filepath = output_dir / item.name.replace(".html", ".md")

        with open(filepath, 'w', encoding='utf-8') as f:
            if translated_chapter.chapter_number and translated_chapter.chapter_title:
                f.write(f'# Chapter {translated_chapter.chapter_number}: {translated_chapter.chapter_title}\n\n')
            elif translated_chapter.chapter_number:
                f.write(f'# Chapter {translated_chapter.chapter_number}\n\n')
            f.write(translated_chapter.translated_text)

        print(f"Translated chapter saved to: {filepath}")


if __name__ == "__main__":
    main()