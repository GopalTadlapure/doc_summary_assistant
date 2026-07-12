import os
import shutil
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

# Dynamic Tesseract path detection on Windows
if os.name == 'nt':
    common_tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe")
    ]
    # If not already available in system PATH, try standard locations
    if not shutil.which("tesseract"):
        for path in common_tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break


def extract_text_from_image(image_path):
    """
    Extracts text from a single image (JPG, PNG, JPEG) using pytesseract.
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except pytesseract.TesseractNotFoundError:
        raise RuntimeError(
            "Tesseract OCR is not installed or not in the system path. "
            "Please check installation instructions in the README.md."
        )
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from image: {str(e)}")


def extract_text_from_pdf_ocr(pdf_path):
    """
    Converts a scanned PDF to images page-by-page and extracts text using OCR.
    """
    try:
        # Convert PDF pages to PIL images
        # Note: pdf2image requires Poppler installed on the system
        try:
            pages = convert_from_path(pdf_path)
        except Exception as e:
            # Check for common poppler error
            if "poppler" in str(e).lower() or "pdfinfo" in str(e).lower():
                raise RuntimeError(
                    "Poppler is required to process scanned PDFs but was not found. "
                    "Please install Poppler and add it to your system PATH as detailed in README.md."
                )
            raise RuntimeError(f"pdf2image conversion failed: {str(e)}")

        full_text = []
        for i, page_image in enumerate(pages):
            try:
                page_text = pytesseract.image_to_string(page_image)
                if page_text.strip():
                    full_text.append(f"--- Page {i + 1} OCR ---\n{page_text}")
            except pytesseract.TesseractNotFoundError:
                raise RuntimeError(
                    "Tesseract OCR is not installed or not in the system path. "
                    "Please check installation instructions in the README.md."
                )

        return "\n\n".join(full_text)
    except Exception as e:
        if isinstance(e, RuntimeError):
            raise e
        raise RuntimeError(f"Scanned PDF OCR failed: {str(e)}")