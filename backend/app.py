import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

from pdf_reader import extract_pdf_text
from ocr import extract_text_from_image, extract_text_from_pdf_ocr
from summarizer import generate_summary
from text_processor import clean_text
from evaluation import calculate_rouge

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return jsonify({
        "status": "healthy",
        "message": "AI Document Summary Assistant Backend Running Successfully",
        "pipeline": "pdfplumber -> Tesseract OCR -> T5-small transformer -> ROUGE evaluation"
    })


@app.route("/upload", methods=["POST"])
def upload():
    # 1. Check if file exists in request
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    # Save uploaded file to the uploads folder
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # 2. Extract options from form data
    summary_length = request.form.get("summaryLength", "short")
    reference_summary = request.form.get("referenceSummary", "")

    # Start timing the process
    start_time = time.time()

    text = ""
    file_ext = os.path.splitext(file.filename.lower())[1]

    try:
        # 3. Extract text / OCR pipeline
        if file_ext == ".pdf":
            # First, try standard digital PDF text extraction
            text = extract_pdf_text(file_path)
            
            # If no text was extracted, fall back to scanned PDF OCR
            if not text.strip():
                print(f"No extractable text found in digital PDF: {file.filename}. Falling back to OCR...")
                text = extract_text_from_pdf_ocr(file_path)
        
        elif file_ext in [".jpg", ".jpeg", ".png"]:
            # Run image OCR
            text = extract_text_from_image(file_path)
        
        else:
            # Clean up saved file and return error for unsupported files
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({
                "success": False,
                "message": f"Unsupported file format: {file_ext}. Supported formats are PDF, JPG, PNG."
            }), 400

        # Clean text
        text = clean_text(text)

        # 4. Check if any text was extracted
        if not text.strip():
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({
                "success": False,
                "message": "No readable text could be extracted or OCR'd from the document."
            }), 200

        # 5. Generate summary
        summary = generate_summary(text, summary_length)

        # Stop timing
        end_time = time.time()
        processing_duration = end_time - start_time
        processing_time_str = f"{processing_duration:.2f}s"

        # Calculate word count of generated summary
        summary_word_count = len(summary.split())
        extracted_word_count = len(text.split())

        # 6. Calculate optional ROUGE evaluation if reference is provided
        rouge_scores = None
        if reference_summary.strip():
            rouge_scores = calculate_rouge(reference_summary.strip(), summary)

        # Clean up uploaded file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

        # 7. Construct API response matching requirements
        response_data = {
            "success": True,
            "filename": file.filename,
            "extracted_text": text,
            "summary": summary,
            "word_count": str(summary_word_count),
            "processing_time": processing_time_str,
            "extracted_word_count": str(extracted_word_count)
        }

        # Include ROUGE scores in response if evaluated
        if rouge_scores:
            response_data["rouge_scores"] = rouge_scores

        return jsonify(response_data)

    except Exception as e:
        # Ensure cleanup of upload file even on failure
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"Pipeline error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"An error occurred during processing: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)