from typing import List

from markitdown import DocumentConverterResult

CHAR_COUNT = 10000


def get_text_chunks(extracted_text: DocumentConverterResult) -> List[str]:
    text = extracted_text.markdown or ""
    if not text.strip():
        return []
    if len(text) <= CHAR_COUNT:
        return [text]

    start = 0
    chunks = []
    while start < len(text):
        raw_end = min(start + CHAR_COUNT, len(text))
        end = text.rfind(" ", start, raw_end) if raw_end < len(text) else raw_end
        if end <= start:
            end = raw_end
        chunks.append(text[start:end])
        start = end + (end < len(text) and text[end] == " ")
    return chunks
