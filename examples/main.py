#!/usr/bin/env python3
"""
Example usage of the Intelligo package for translating HTML files.

This script demonstrates how to:
1. Process HTML files from an input directory
2. Translate web novel chapters using the Intelligo class
3. Save translated content to an output directory
4. Handle errors and provide progress feedback

Prerequisites:
1. Set the GEMINI_API_KEY environment variable
2. Install dependencies: pip install -r requirements.txt
3. Ensure HTML files are in the input directory
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
from intelligo import Intelligo
from intelligo.exceptions import ConfigNotLoadedError, ScraperError

def setup_environment() -> bool:
    """
    Check if the required environment variables are set.
    
    Returns:
        bool: True if environment is properly configured, False otherwise
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable is not set.")
        print("Please set it with: export GEMINI_API_KEY='your-api-key-here'")
        return False
    
    print("✅ Environment configured successfully")
    return True

def get_html_files(input_dir: Path) -> List[Path]:
    """
    Get all HTML files from the input directory.
    
    Args:
        input_dir: Path to the directory containing HTML files
        
    Returns:
        List of Path objects for HTML files
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory '{input_dir}' does not exist")
    
    html_files = list(input_dir.glob("*.html"))
    html_files.extend(input_dir.glob("*.htm"))
    
    # Sort files naturally (e.g., chapter1.html, chapter2.html, ...)
    html_files.sort(key=lambda x: x.name.lower())
    
    return html_files

def create_output_directory(output_dir: Path) -> None:
    """
    Create the output directory if it doesn't exist.
    
    Args:
        output_dir: Path to the output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory ready: {output_dir}")

def translate_single_file(
    html_file: Path, 
    output_dir: Path, 
    additional_instructions: Optional[str] = None
) -> bool:
    """
    Translate a single HTML file using Intelligo.
    
    Args:
        html_file: Path to the HTML file to translate
        output_dir: Directory to save the translated content
        additional_instructions: Optional additional translation instructions
        
    Returns:
        bool: True if translation was successful, False otherwise
    """
    try:
        print(f"🔄 Processing: {html_file.name}")
        
        # Initialize Intelligo with the HTML file
        translator = Intelligo(
            input_file=html_file,
            additional_instructions=additional_instructions
        )
        
        # Translate the chapter
        translated_chapter = translator.translate_chapter()
        
        # Create output filename (replace .html with .md)
        output_filename = html_file.stem + ".md"
        output_file = output_dir / output_filename
        
        # Save the translated content
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(translated_chapter.content)
        
        print(f"✅ Successfully translated: {html_file.name} -> {output_filename}")
        print(f"   Novel: {translated_chapter.novel_title}")
        if translated_chapter.chapter_title:
            print(f"   Chapter: {translated_chapter.chapter_title}")
        print(f"   Chapter Number: {translated_chapter.number}")
        
        return True
        
    except ConfigNotLoadedError as e:
        print(f"❌ Configuration error: {e}")
        return False
    except ScraperError as e:
        print(f"❌ Translation error for {html_file.name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error processing {html_file.name}: {e}")
        return False

def main():
    """
    Main function to process HTML files from input directory and translate them.
    """
    print("🚀 Intelligo HTML Translation Example")
    print("=" * 50)
    
    # Check environment setup
    if not setup_environment():
        return sys.exit(1)
    
    # Configuration
    input_directory = Path("input_html")  # Directory containing HTML files
    output_directory = Path("translated_chapters")  # Directory for translated output
    
    # Optional: Add custom translation instructions
    additional_instructions = """
    Please maintain consistent character names throughout the translation.
    Use modern, natural English while preserving the original tone and style.
    Keep cultural references but add brief explanations if necessary.
    """
    
    try:
        # Get all HTML files from input directory
        html_files = get_html_files(input_directory)
        
        if not html_files:
            print(f"⚠️  No HTML files found in '{input_directory}'")
            print("Please add HTML files to the input directory and try again.")
            return
        
        print(f"📚 Found {len(html_files)} HTML file(s) to process")
        
        # Create output directory
        create_output_directory(output_directory)
        
        # Process each HTML file
        successful_translations = 0
        failed_translations = 0
        
        for i, html_file in enumerate(html_files, 1):
            print(f"\n[{i}/{len(html_files)}] Processing file...")
            
            success = translate_single_file(
                html_file=html_file,
                output_dir=output_directory,
                additional_instructions=additional_instructions
            )
            
            if success:
                successful_translations += 1
            else:
                failed_translations += 1
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Translation Summary")
        print(f"✅ Successful: {successful_translations}")
        print(f"❌ Failed: {failed_translations}")
        print(f"📁 Output directory: {output_directory.absolute()}")
        
        if successful_translations > 0:
            print(f"🎉 Translation completed! Check '{output_directory}' for results.")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print(f"Please create the '{input_directory}' directory and add HTML files to it.")
    except KeyboardInterrupt:
        print("\n⏹️  Translation interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    # Example of how to use the script with different configurations
    
    # Option 1: Use default settings (uncomment to use)
    main()
    
    # Option 2: Custom directory paths (uncomment and modify to use)
    # input_dir = Path("my_novels/raw_html")
    # output_dir = Path("my_novels/translated")
    # # ... modify main() function to use these paths
    
    # Option 3: Process a single file (uncomment to use)
    # single_file = Path("input_html/chapter001.html")
    # output_dir = Path("translated_chapters")
    # if single_file.exists():
    #     create_output_directory(output_dir)
    #     translate_single_file(single_file, output_dir)