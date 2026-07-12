import os
import re
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from text_processor import clean_text, chunk_text

# Define path for local model storage
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(CURRENT_DIR, "models", "t5-small")

print("Initializing local Hugging Face T5-small summarizer...")
print(f"Model directory: {MODEL_DIR}")

# Download and save model locally if not already present
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

# Load tokenizer and model from local folder
local_tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
local_model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR)

# Initialize the pipeline with local model and tokenizer
summarization_pipeline = pipeline(
    "summarization",
    model=local_model,
    tokenizer=local_tokenizer
)


def post_process_summary(text):
    """
    Post-processes raw T5 model output into clean, readable text:
    - Capitalizes the first letter of every sentence
    - Ensures the summary ends with a period
    - Removes duplicate/repeated phrases
    - Normalizes whitespace
    """
    if not text:
        return text

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Split into sentences and capitalize each one
    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_endings.split(text)
    capitalized = []
    for s in sentences:
        s = s.strip()
        if s:
            s = s[0].upper() + s[1:]
            capitalized.append(s)
    text = ' '.join(capitalized)

    # Capitalize after dash/em-dash as well: "– cloud" -> "– Cloud"
    text = re.sub(r'([–—]\s*)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)

    # Ensure sentence ends with a period if missing
    if text and text[-1] not in '.!?':
        text += '.'

    # Remove duplicate consecutive words (e.g. "the the cloud" -> "the cloud")
    text = re.sub(r'\b(\w+)( \1)+\b', r'\1', text, flags=re.IGNORECASE)

    return text


def summarize_chunk(text, max_len=150, min_len=30):
    """
    Summarizes a single text chunk using the T5 model.
    T5 models require the prefix 'summarize: ' before the text.
    Enforces strict 512-token input truncation to prevent model overflow errors.
    """
    # Prepend T5 task prefix
    input_text = "summarize: " + text

    try:
        # Tokenize with strict truncation to 512 tokens (T5's maximum input length)
        # This prevents the '591 > 512' indexing error warning
        tokens = local_tokenizer(
            input_text,
            max_length=512,
            truncation=True,
            return_tensors="pt"
        )

        # Decode the truncated tokens back to text for the pipeline
        truncated_text = local_tokenizer.decode(
            tokens["input_ids"][0],
            skip_special_tokens=True
        )

        # Generate summary from the safely-truncated input
        result = summarization_pipeline(
            truncated_text,
            max_length=max_len,
            min_length=min(min_len, max_len - 1),
            do_sample=False
        )
        raw = result[0]["summary_text"]
        return post_process_summary(raw)
    except Exception as e:
        print(f"Error during chunk summarization: {str(e)}")
        return text


def generate_summary(text, length="short"):
    """
    Generates an abstractive summary of the given text using the local T5 model.
    Implements a recursive chunk-and-summarize workflow for large documents.
    """
    # Clean text first
    cleaned_text = clean_text(text)
    if not cleaned_text:
        return "No text available to summarize."

    # Determine word count
    words = cleaned_text.split()
    word_count = len(words)
    
    # Target length configurations
    if length == "short":
        target_max = 80
        target_min = 30
    elif length == "medium":
        target_max = 150
        target_min = 60
    else:  # long
        target_max = 250
        target_min = 100

    # Max chunk size in words. 250 words is conservative because T5 tokenizes
    # some words into multiple sub-tokens (~1.4x ratio), so 250 words ~ 350 tokens,
    # well within the 512-token limit after adding the 'summarize: ' prefix.
    MAX_CHUNK_WORDS = 250

    # If the document is small enough, summarize it directly in one go
    if word_count <= MAX_CHUNK_WORDS:
        return summarize_chunk(cleaned_text, max_len=target_max, min_len=target_min)

    # Document is large: split into chunks and summarize each chunk
    print(f"Document word count ({word_count}) exceeds chunk limit ({MAX_CHUNK_WORDS}). Chunking...")
    chunks = chunk_text(cleaned_text, max_words=MAX_CHUNK_WORDS)
    print(f"Split into {len(chunks)} chunks.")

    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        # We summarize intermediate chunks to a medium size so we don't lose too much context
        chunk_sum = summarize_chunk(chunk, max_len=120, min_len=40)
        chunk_summaries.append(chunk_sum)
        print(f"Summarized chunk {i+1}/{len(chunks)}")

    # Combine chunk summaries
    combined_summary_text = " ".join(chunk_summaries)
    
    # If the combined summary text is still larger than the chunk size, recursively summarize it
    combined_words = combined_summary_text.split()
    if len(combined_words) > MAX_CHUNK_WORDS:
        print(f"Combined summary word count ({len(combined_words)}) is still too large. Recursively summarizing...")
        return generate_summary(combined_summary_text, length=length)

    # Final summarization to the target length
    print(f"Generating final summary of length: {length}")
    final_summary = summarize_chunk(combined_summary_text, max_len=target_max, min_len=target_min)
    return final_summary