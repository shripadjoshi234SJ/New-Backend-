from typing import Optional

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - fallback for environments without pypdf
    PdfReader = None


async def extract_text_from_pdf(file_path: str) -> str:
    if PdfReader is None:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()

    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        text_parts.append(text)
    return "\n".join(text_parts).strip()
