from intelligo import Intelligo
from pathlib import Path
output_dir = Path("output")

# i = Intelligo(input_file, output_dir)
# ch = i.translate_chapter()

input_path = Path(__file__).resolve().parent / "input"
input_files = list(input_path.glob("*.html"))

for input_file in input_files:
    i = Intelligo(input_file)
    ch = i.translate_chapter()
    output_file = output_dir / ch.novel_title / f"ch-{ch.number}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(ch.content)