import os
import re
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from text_processor import clean_text, chunk_text

# ==============================
# Local Model Directory
# ==============================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(CURRENT_DIR, "models", "t5-small")

print("Initializing local Hugging Face T5-small summarizer...")
print(f"Model directory: {MODEL_DIR}")

# Download model once
if not os.path.exists(MODEL_DIR) or not os.listdir(MODEL_DIR):
    os.makedirs(MODEL_DIR, exist_ok=True)

    print("Local model not found. Downloading T5-small from Hugging Face...")

    tokenizer = AutoTokenizer.from_pretrained("t5-small")
    model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")

    tokenizer.save_pretrained(MODEL_DIR)
    model.save_pretrained(MODEL_DIR)

    print("Model downloaded and saved locally.")

else:
    print("Loading model from local directory...")

# ==============================
# Load Model
# ==============================

local_tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

local_model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR)

local_model.eval()

summarization_pipeline = pipeline(
    "summarization",
    model=local_model,
    tokenizer=local_tokenizer,
    device=-1
)

# ==============================
# Post Processing
# ==============================

def post_process_summary(text):

    if not text:
        return text

    text = re.sub(r"\s+", " ", text).strip()

    sentence_endings = re.compile(r"(?<=[.!?])\s+")

    sentences = sentence_endings.split(text)

    processed = []

    for s in sentences:

        s = s.strip()

        if s:

            s = s[0].upper() + s[1:]

            processed.append(s)

    text = " ".join(processed)

    text = re.sub(
        r"([–—]\s*)([a-z])",
        lambda m: m.group(1) + m.group(2).upper(),
        text,
    )

    if text and text[-1] not in ".!?":
        text += "."

    text = re.sub(
        r"\b(\w+)( \1)+\b",
        r"\1",
        text,
        flags=re.IGNORECASE,
    )

    return text

# ==============================
# Summarize One Chunk
# ==============================

def summarize_chunk(text, max_len=80, min_len=25):

    input_text = "summarize: " + text

    try:

        tokens = local_tokenizer(
            input_text,
            max_length=512,
            truncation=True,
            return_tensors="pt",
        )

        truncated_text = local_tokenizer.decode(
            tokens["input_ids"][0],
            skip_special_tokens=True,
        )

        result = summarization_pipeline(
            truncated_text,
            max_length=max_len,
            min_length=min(min_len, max_len - 1),
            do_sample=False,
            num_beams=1,
            early_stopping=True,
            length_penalty=1.0,
        )

        summary = result[0]["summary_text"]

        return post_process_summary(summary)

    except Exception as e:

        print("Summarization Error:", e)

        return text

# ==============================
# Main Summary Function
# ==============================

def generate_summary(text, length="short"):

    cleaned_text = clean_text(text)

    if not cleaned_text:

        return "No text available."

    words = cleaned_text.split()

    word_count = len(words)

    # Faster summary sizes

    if length == "short":

        target_max = 50
        target_min = 20

    elif length == "medium":

        target_max = 80
        target_min = 35

    else:

        target_max = 120
        target_min = 50

    # Smaller chunks for Railway

    MAX_CHUNK_WORDS = 150

    # Small document

    if word_count <= MAX_CHUNK_WORDS:

        return summarize_chunk(
            cleaned_text,
            target_max,
            target_min,
        )

    print(
        f"Document word count ({word_count}) exceeds chunk limit ({MAX_CHUNK_WORDS})."
    )

    chunks = chunk_text(
        cleaned_text,
        max_words=MAX_CHUNK_WORDS,
    )

    print(f"Split into {len(chunks)} chunks.")

    chunk_summaries = []

    for i, chunk in enumerate(chunks):

        print(f"Summarizing chunk {i+1}/{len(chunks)}")

        chunk_summary = summarize_chunk(
            chunk,
            max_len=60,
            min_len=20,
        )

        chunk_summaries.append(chunk_summary)

    combined_summary = " ".join(chunk_summaries)

    if len(combined_summary.split()) > MAX_CHUNK_WORDS:

        print("Recursively summarizing combined summary...")

        return generate_summary(
            combined_summary,
            length,
        )

    print("Generating final summary...")

    final_summary = summarize_chunk(
        combined_summary,
        target_max,
        target_min,
    )

    return final_summary