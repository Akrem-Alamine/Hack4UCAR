"""
Track 1 — PDF/image OCR extraction pipeline.
Handles both text-native PDFs (pdfplumber) and scanned/image PDFs (pytesseract).
"""
import io
import os
from pathlib import Path


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file. Falls back to OCR if no selectable text found."""
    import pdfplumber

    text_pages = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text and len(page_text.strip()) > 20:
                text_pages.append(page_text)
            else:
                # Scanned page — extract as image and OCR
                ocr_text = _ocr_page(page)
                if ocr_text:
                    text_pages.append(ocr_text)

    return "\n\n".join(text_pages)


def _ocr_page(page) -> str:
    """Render a pdfplumber page as image and run Tesseract OCR."""
    try:
        import pytesseract
        from PIL import Image

        # Render at 200 DPI for decent OCR quality
        img = page.to_image(resolution=200).original
        text = pytesseract.image_to_string(img, lang="fra+ara+eng")
        return text.strip()
    except Exception:
        return ""


def extract_text_from_image(file_bytes: bytes, filename: str = "") -> str:
    """Run OCR on a standalone image file (PNG, JPG, etc.)."""
    try:
        import pytesseract
        from PIL import Image

        img = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(img, lang="fra+ara+eng")
        return text.strip()
    except Exception as e:
        return f"[OCR error: {e}]"


def extract_text(file_bytes: bytes, filename: str) -> tuple[str, str]:
    """
    Route file to the right extractor based on extension.
    Returns (extracted_text, method_used).
    """
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        text = extract_text_from_pdf(file_bytes)
        return text, "pdf+ocr"
    elif ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif", ".webp"}:
        text = extract_text_from_image(file_bytes, filename)
        return text, "ocr"
    else:
        return "", "unsupported"
