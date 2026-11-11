from pathlib import Path
from markitdown import MarkItDown, DocumentConverterResult


def extract_files(paths: list[Path]) -> list[DocumentConverterResult]:
    extracted_text = []
    md = MarkItDown()
    for path in paths:
        extracted_text.append(md.convert(path))
    return extracted_text



