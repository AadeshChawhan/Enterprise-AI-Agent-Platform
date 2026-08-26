from pathlib import Path

from docx import Document
from pypdf import PdfReader


def extract_text_from_txt(
    file_path: str,
) -> str:
    path = Path(file_path)

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def extract_text_from_pdf(
    file_path: str,
) -> str:
    reader = PdfReader(
        file_path
    )

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n\n".join(pages)


def extract_text_from_docx(
    file_path: str,
) -> str:
    document = Document(
        file_path
    )

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs)


def extract_text(
    file_path: str,
) -> str:
    path = Path(file_path)

    extension = path.suffix.lower()

    if extension == ".txt":
        text = extract_text_from_txt(
            file_path
        )

    elif extension == ".pdf":
        text = extract_text_from_pdf(
            file_path
        )

    elif extension == ".docx":
        text = extract_text_from_docx(
            file_path
        )

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    text = text.strip()

    if not text:
        raise ValueError(
            "No readable text was found in the document"
        )

    return text

def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative"
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    cleaned_text = " ".join(
        text.split()
    )

    if not cleaned_text:
        return []

    chunks = []

    start = 0

    while start < len(cleaned_text):
        end = start + chunk_size

        chunk = cleaned_text[
            start:end
        ].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(cleaned_text):
            break

        start = end - overlap

    return chunks


def extract_and_chunk(
    file_path: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[str]:
    text = extract_text(
        file_path
    )

    return chunk_text(
        text=text,
        chunk_size=chunk_size,
        overlap=overlap,
    )