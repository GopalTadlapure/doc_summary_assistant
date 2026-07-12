import re

# --------------------------------------------------------------------------
# Word Segmentation (handles concatenated words from PDF extraction)
# --------------------------------------------------------------------------

_wordsegment_loaded = False

def _load_wordsegment():
    """Lazily load wordsegment corpus — done once per server session."""
    global _wordsegment_loaded
    if not _wordsegment_loaded:
        try:
            from wordsegment import load
            load()
            _wordsegment_loaded = True
            print("[text_processor] wordsegment corpus loaded.")
        except Exception as e:
            print(f"[text_processor] wordsegment unavailable: {e}")


def fix_concatenated_words(text):
    """
    Uses regex to find long runs of alphabetic characters (8+ chars) in the text
    and applies wordsegment to intelligently split them.

    This handles both:
      CamelCase:  "AWSAcademyGraduate"                    -> "AWS Academy Graduate"
      Lowercase:  "scienceundergraduatewithstrongfoundations" -> "science undergraduate with strong foundations"

    wordsegment is smart enough to leave real English words (e.g. "programming",
    "development", "undergraduate") intact while splitting concatenated ones.
    """
    _load_wordsegment()

    def segment_match(match):
        word = match.group(0)
        try:
            from wordsegment import segment
            parts = segment(word.lower())
            if not parts:
                return word
            result = ' '.join(parts)
            # Restore capitalisation of the first letter if original was capitalised
            if word[0].isupper() and result:
                result = result[0].upper() + result[1:]
            return result
        except Exception:
            return word

    # Match sequences of 10+ consecutive alphabetic characters.
    # Skip words that wordsegment returns unchanged (i.e. real single English words).
    return re.sub(r'[A-Za-z]{10,}', segment_match, text)


def fix_spacing_artifacts(text):
    """
    Fixes PDF extraction artifacts around digits and special chars:
      "March2026"  -> "March 2026"
      "2026Amazon" -> "2026 Amazon"
      "94%score"   -> "94% score"
    """
    text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
    text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
    text = re.sub(r'([%–—])([a-zA-Z])', r'\1 \2', text)
    return text


# --------------------------------------------------------------------------
# Main Clean Function
# --------------------------------------------------------------------------

def clean_text(text):
    """
    Full text cleaning pipeline for PDF / OCR extracted text:
      1. Insert spaces around commas embedded inside long concatenated words
      2. Fix concatenated words (CamelCase and all-lowercase merges) via wordsegment
      3. Fix digit-letter and symbol-letter spacing artifacts
      4. Normalize all whitespace to single spaces
    """
    if not text:
        return ""

    # Step 1: Insert spaces around commas that appear inside concatenated runs.
    # e.g. "development,datastructures,andcloud" -> "development, datastructures, andcloud"
    # Pattern: comma between two alphabetic characters with no surrounding spaces
    text = re.sub(r'(?<=[a-zA-Z]),(?=[a-zA-Z])', ', ', text)

    # Step 2: Segment concatenated alphabetic sequences using wordsegment
    text = fix_concatenated_words(text)

    # Step 3: Fix digit/symbol spacing
    text = fix_spacing_artifacts(text)

    # Step 4: Collapse all whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# --------------------------------------------------------------------------
# Sentence Splitting & Chunking
# --------------------------------------------------------------------------

def split_sentences_regex(text):
    """Regex fallback sentence splitter used when NLTK is unavailable."""
    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_endings.split(text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text, max_words=250):
    """
    Splits cleaned text into sentence-aligned chunks of at most max_words.

    250 words is chosen conservatively:
      T5 sub-word tokenisation means 250 words ≈ 350 tokens,
      safely within the 512-token input limit even after the 'summarize: ' prefix.
    """
    cleaned_text = clean_text(text)
    if not cleaned_text:
        return []

    # Sentence tokenisation
    try:
        import nltk
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt_tab', quiet=True)
                nltk.download('punkt', quiet=True)
        sentences = nltk.sent_tokenize(cleaned_text)
    except Exception:
        sentences = split_sentences_regex(cleaned_text)

    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        words = sentence.split()
        num_words = len(words)
        if num_words == 0:
            continue

        if num_words > max_words:
            # Flush existing chunk before splitting this oversized sentence
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_word_count = 0
            for i in range(0, num_words, max_words):
                chunks.append(" ".join(words[i:i + max_words]))
        else:
            if current_word_count + num_words > max_words:
                chunks.append(" ".join(current_chunk))
                current_chunk = words
                current_word_count = num_words
            else:
                current_chunk.extend(words)
                current_word_count += num_words

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
