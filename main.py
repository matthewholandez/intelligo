from intelligo import Intelligo
from pathlib import Path

input_file = Path("test.html")
output_dir = Path("output")

i = Intelligo(input_file, output_dir)
thing = i.scrape_chapter()
print(thing["novel_title"])