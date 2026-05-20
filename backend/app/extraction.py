import trafilatura


def extract_text_from_html(html: str) -> str:
    text = trafilatura.extract(html)
    if not text:
        raise ValueError("Could not extract text from HTML")
    return text
