from intelligo.scraper import scrape
from pathlib import Path

print(scrape(Path(__file__).parent / 'test.html'))