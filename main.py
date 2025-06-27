from intelligo import Intelligo
from pathlib import Path

input_file = Path("test.html")
output_dir = Path("output")

i = Intelligo(input_file, output_dir)
ch = i.translate_chapter()
print(ch.content)
print(ch.chapter_title)
print(ch.novel_title)
print(ch.number)