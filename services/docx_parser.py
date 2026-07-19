try:
    from docx import Document
except ImportError:  # pragma: no cover - fallback for environments without python-docx
    Document = None


async def extract_text_from_docx(file_path: str) -> str:
    if Document is None:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()

    doc = Document(file_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)
