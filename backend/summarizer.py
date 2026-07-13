import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from text_processor import clean_text, chunk_text

# ============================================================
# Torch Thread Config (avoid CPU thread contention on small
# Railway containers, which can slow down generate() calls)
# ============================================================

torch.set_num_threads(2)

# ============================================================
# Local Model Directory
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(CURRENT_DIR, "models", "t5-small")

print("Initializing local Hugging Face T5-small summarizer...")
print(f"Model directory: {MODEL_DIR}")

if not os.path.exists(MODEL_DIR) or not os.listdir(MODEL_DIR):

    os.makedirs(MODEL_DIR, exist_ok=True)

    print("Downloading T5-small model...")

    tokenizer = AutoTokenizer.from_pretrained("t5-small")
    model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")

    tokenizer.save_pretrained(MODEL_DIR)
    model.save_pretrained(MODEL_DIR)

    print("Download complete.")

else:

    print("Loading local model...")

local_tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
local_model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR)

local_model.eval()

# ============================================================
# Summary Cleanup
# ============================================================

def post_process_summary(text):

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text).strip()

    sentence_endings = re.compile(r"(?<=[.!?])\s+")

    sentences = sentence_endings.split(text)

    cleaned = []

    for sentence in sentences:

        sentence = sentence.strip()

        if sentence:

            sentence = sentence[0].upper() + sentence[1:]

            cleaned.append(sentence)

    text = " ".join(cleaned)

    text = re.sub(
        r"\b(\w+)( \1)+\b",
        r"\1",
        text,
        flags=re.IGNORECASE,
    )

    if text and text[-1] not in ".!?":
        text += "."

    return text

# ============================================================
# Summarize One Chunk
# ============================================================

def summarize_chunk(text, max_len=80, min_len=25):

    if not text.strip():
        return ""

    try:

        input_text = "summarize: " + text

        # Reduced from 512 -> 200. Chunks are capped at ~100 words
        # (roughly 130-150 tokens), so 512 was doing unnecessary
        # padding/attention work on every call.
        tokens = local_tokenizer(
            input_text,
            max_length=200,
            truncation=True,
            return_tensors="pt",
        )

        with torch.inference_mode():

            summary_ids = local_model.generate(
                tokens["input_ids"],
                attention_mask=tokens["attention_mask"],
                max_length=max_len,
                min_length=min_len,
                num_beams=1,
                do_sample=False,
                early_stopping=True,
                no_repeat_ngram_size=3,
                length_penalty=1.0,
            )

        summary = local_tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True,
        )

        return post_process_summary(summary)

    except Exception as e:

        print("Summarization Error:", e)

        return text

# ============================================================
# Main Summary Function
# ============================================================

def generate_summary(text, length="short"):

    cleaned_text = clean_text(text)

    if not cleaned_text.strip():
        return "No text available to summarize."

    word_count = len(cleaned_text.split())

    # Target summary lengths
    if length == "short":
        target_max = 50
        target_min = 20

    elif length == "medium":
        target_max = 80
        target_min = 35

    else:
        target_max = 100
        target_min = 45

    # Smaller chunks for Railway CPU
    MAX_CHUNK_WORDS = 100

    # Small document
    if word_count <= MAX_CHUNK_WORDS:
        return summarize_chunk(
            cleaned_text,
            max_len=target_max,
            min_len=target_min,
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

        summary = summarize_chunk(
            chunk,
            max_len=40,
            min_len=15,
        )

        chunk_summaries.append(summary)

    combined_summary = " ".join(chunk_summaries)

    # Recursive summarization if still too long
    while len(combined_summary.split()) > MAX_CHUNK_WORDS:

        print("Combined summary still large. Summarizing again...")

        smaller_chunks = chunk_text(
            combined_summary,
            max_words=MAX_CHUNK_WORDS,
        )

        temp = []

        for chunk in smaller_chunks:

            temp.append(
                summarize_chunk(
                    chunk,
                    max_len=35,
                    min_len=15,
                )
            )

        combined_summary = " ".join(temp)

    # Skip the extra final generate() pass if the combined summary
    # is already within the target length -- this was previously
    # forcing a 3rd model.generate() call on every multi-chunk doc,
    # which was a major contributor to the worker timeout.
    if len(combined_summary.split()) <= target_max:
        return post_process_summary(combined_summary)

    print("Generating final summary...")

    final_summary = summarize_chunk(
        combined_summary,
        max_len=target_max,
        min_len=target_min,
    )

    return final_summary