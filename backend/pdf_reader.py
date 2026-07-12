import pdfplumber

def extract_pdf_text(pdf_path):
    """
    Attempts to extract text from a PDF file using pdfplumber.
    Returns the extracted text as a string, or an empty string if no text is found.
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise RuntimeError(f"Error opening or reading PDF file: {str(e)}")

    return text.strip()