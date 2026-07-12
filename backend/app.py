import os
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from pdf_reader import extract_pdf_text
from ocr import extract_text_from_image, extract_text_from_pdf_ocr
from summarizer import generate_summary
from text_processor import clean_text
from evaluation import calculate_rouge


app = Flask(__name__)
CORS(app)


# =========================
# Upload folder
# =========================

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# =========================
# React Frontend Path
# =========================

FRONTEND_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "frontend",
    "dist"
)


# =========================
# Serve React Frontend
# =========================

@app.route("/")
def serve_frontend():
    if os.path.exists(os.path.join(FRONTEND_FOLDER, "index.html")):
        return send_from_directory(FRONTEND_FOLDER, "index.html")

    return jsonify({
        "status": "healthy",
        "message": "AI Document Summary Assistant Backend Running Successfully"
    })


# =========================
# Backend Health Check
# =========================

@app.route("/api")
def api_status():
    return jsonify({
        "status": "healthy",
        "message": "Backend Running Successfully",
        "pipeline": "pdfplumber -> Tesseract OCR -> T5-small transformer -> ROUGE evaluation"
    })


# =========================
# Upload API
# =========================

@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No file uploaded"
        }), 400


    file = request.files["file"]


    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400



    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )


    file.save(file_path)



    summary_length = request.form.get(
        "summaryLength",
        "short"
    )


    reference_summary = request.form.get(
        "referenceSummary",
        ""
    )


    start_time = time.time()


    try:

        text = ""

        file_ext = os.path.splitext(
            file.filename.lower()
        )[1]


        # PDF Processing

        if file_ext == ".pdf":

            text = extract_pdf_text(file_path)


            if not text.strip():

                print(
                    "No PDF text found. Running OCR..."
                )

                text = extract_text_from_pdf_ocr(
                    file_path
                )


        # Image Processing

        elif file_ext in [
            ".jpg",
            ".jpeg",
            ".png"
        ]:

            text = extract_text_from_image(
                file_path
            )


        else:

            return jsonify({
                "success": False,
                "message": "Unsupported file format"
            }),400



        # Clean extracted text

        text = clean_text(text)



        if not text.strip():

            return jsonify({
                "success":False,
                "message":"No readable text found"
            }),200



        # Generate summary

        summary = generate_summary(
            text,
            summary_length
        )



        processing_time = (
            time.time() - start_time
        )



        summary_word_count = len(
            summary.split()
        )


        extracted_word_count = len(
            text.split()
        )



        rouge_scores = None


        if reference_summary.strip():

            rouge_scores = calculate_rouge(
                reference_summary,
                summary
            )



        response = {

            "success":True,

            "filename":file.filename,

            "summary":summary,

            "extracted_text":text,

            "word_count":str(
                summary_word_count
            ),

            "extracted_word_count":str(
                extracted_word_count
            ),

            "processing_time":
            f"{processing_time:.2f}s"
        }



        if rouge_scores:

            response["rouge_scores"] = rouge_scores



        return jsonify(response)



    except Exception as e:


        print(
            "Pipeline Error:",
            str(e)
        )


        return jsonify({

            "success":False,

            "message":str(e)

        }),500



    finally:

        # Remove uploaded file

        if os.path.exists(file_path):

            os.remove(file_path)



# =========================
# Railway Start
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )