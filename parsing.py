import fitz  # PyMuPDF
from docx import Document
from pathlib import Path

def read_pdf(path: str) -> str:
    text = []
    with fitz.open(path) as doc:
        for page in doc:
            text.append(page.get_text("text"))
    return "\n".join(text)

def read_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text(path: str) -> str:
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        return read_pdf(str(p))
    if p.suffix.lower() in [".docx", ".doc"]:
        return read_docx(str(p))
    raise ValueError(f"Unsupported file: {p.suffix}")
