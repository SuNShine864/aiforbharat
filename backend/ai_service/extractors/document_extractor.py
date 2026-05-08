"""
document_extractor.py
Extracts plain text from:
  - PDF (digital text via PyMuPDF, fallback to OCR per page)
  - DOCX (python-docx)
  - Images (JPG/PNG/TIFF → pytesseract OCR)
Output format (list of dicts):
[
  {"page": 1, "text": "..."},
  {"page": 2, "text": "..."}
]
"""
import cv2
import os
import fitz          # PyMuPDF
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from PIL import Image
from docx import Document as DocxDocument


def extract_text_from_file(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_pdf(file_path)

    elif ext == ".docx":
        return _extract_docx(file_path)

    elif ext in (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"):
        return _ocr_image(file_path)

    else:
        print("Unsupported file type:", ext)
        return []


def _extract_pdf(path: str):
    """
    Extract page-wise text from PDF.
    Uses OCR if page has very little text.
    """
    doc = fitz.open(path)
    data = []

    for i, page in enumerate(doc):
        page_no = i + 1
        text = page.get_text("text").strip()

        if len(text) < 50:
            try:
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img, lang="eng")
            except:
                text = ""

        data.append({
            "source_type": "pdf",
            "page": page_no,
            "block": 1,   # whole page = one block
            "text": text.strip()
        })

    doc.close()
    print("LLM API GENERATED",data)
    return data

def _extract_docx(path: str) -> str:
    doc = DocxDocument(path)
    data = []

    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if text:
            data.append({
                "source_type": "docx",
                "page": None,          # no real page
                "block": i + 1,        # paragraph index
                "text": text
            })

    return data


def _ocr_image(path: str) -> list:
    try:
        # Load using OpenCV
        img = cv2.imread(path)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply threshold (important)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # OCR with better config
        text = pytesseract.image_to_string(
            thresh,
            lang="eng",
            config="--psm 6"
        )

    except Exception as e:
        print("OCR error:", e)
        text = ""

    return [{
        "source_type": "image",
        "page": None,   # better for images
        "block": 1,
        "text": text.strip()
    }]