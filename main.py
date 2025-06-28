#!/usr/bin/env python3
"""
Novel Translation Processor

A script to batch process and translate web novel chapters from HTML files
using the Intelligo translation library.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from intelligo import Intelligo
from intelligo.exceptions import ConfigNotLoadedError, ScraperError


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with appropriate level and format."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_input_files(input_dir: Path, pattern: str = "*.html") -> List[Path]:
    """
    Get all HTML files from the input directory.
    
    Args:
        input_dir: Directory containing input files
        pattern: File pattern to match (default: "*.html")
        
    Returns:
        List of Path objects for matching files
        
    Raises:
        FileNotFoundError: If input directory doesn't exist
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory '{input_dir}' not found")
    
    files = list(input_dir.glob(pattern))
    if not files:
        logging.warning(f"No files matching '{pattern}' found in '{input_dir}'")
    
    return files


def process_single_file(input_file: Path, output_dir: Path, force: bool = False) -> bool:
    """
    Process a single HTML file through the translation pipeline.
    
    Args:
        input_file: Path to the input HTML file
        output_dir: Directory for output files
        force: Whether to overwrite existing translations
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize Intelligo with the input file
        intelligo = Intelligo(input_file)
        
        # Scrape chapter information
        scraped_chapter = intelligo.scrape_chapter()
        novel_title = scraped_chapter.novel_title
        chapter_number = scraped_chapter.number
        
        # Determine output file path
        output_file = output_dir / novel_title / f"ch-{chapter_number}.md"
        
        # Check if file already exists
        if output_file.exists() and not force:
            logger.info(f"⏭️  Skipping '{input_file.name}' - translation already exists")
            return True
        
        logger.info(f"🔄 Processing '{input_file.name}' -> Chapter {chapter_number}")
        
        # Translate the chapter
        translated_chapter = intelligo.translate_chapter()
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the translated content
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(translated_chapter.content)
        
        logger.info(f"✅ Successfully translated '{novel_title}' Chapter {chapter_number}")
        return True
        
    except (ConfigNotLoadedError, ScraperError) as e:
        logger.error(f"❌ Translation error for '{input_file.name}': {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error processing '{input_file.name}': {e}")
        return False


def main() -> int:
    """Main entry point for the translation processor."""
    parser = argparse.ArgumentParser(
        description="Batch translate web novel chapters from HTML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Process all HTML files in ./input/
  %(prog)s -i custom_input/         # Use custom input directory
  %(prog)s -o translations/         # Use custom output directory
  %(prog)s --force                  # Overwrite existing translations
  %(prog)s --verbose                # Enable debug logging
        """
    )
    
    parser.add_argument(
        "-i", "--input-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "input",
        help="Input directory containing HTML files (default: ./input/)"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("output"),
        help="Output directory for translated files (default: ./output/)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing translation files"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Get input files
        input_files = get_input_files(args.input_dir)
        
        if not input_files:
            logger.error("No HTML files found to process")
            return 1
        
        logger.info(f"🚀 Starting translation of {len(input_files)} files")
        logger.info(f"📁 Input: {args.input_dir}")
        logger.info(f"📁 Output: {args.output_dir}")
        
        # Process each file
        successful = 0
        failed = 0
        
        for i, input_file in enumerate(input_files, 1):
            logger.info(f"📚 Processing file {i}/{len(input_files)}: {input_file.name}")
            
            if process_single_file(input_file, args.output_dir, args.force):
                successful += 1
            else:
                failed += 1
        
        # Report summary
        logger.info(f"🎉 Translation complete!")
        logger.info(f"✅ Successful: {successful}")
        if failed > 0:
            logger.warning(f"❌ Failed: {failed}")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("🛑 Translation interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())