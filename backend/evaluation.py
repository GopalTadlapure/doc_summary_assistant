from rouge_score import rouge_scorer

def calculate_rouge(reference_summary, generated_summary):
    """
    Calculates ROUGE-1, ROUGE-2, and ROUGE-L scores (precision, recall, and F1-score)
    between a reference summary and the generated summary.
    """
    # If either summary is empty, return zero scores
    if not reference_summary.strip() or not generated_summary.strip():
        zero_score = {"precision": 0.0, "recall": 0.0, "f1-score": 0.0}
        return {
            "rouge-1": zero_score,
            "rouge-2": zero_score,
            "rouge-l": zero_score
        }

    # Initialize the RougeScorer with the metrics we want
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    # Calculate scores
    scores = scorer.score(reference_summary, generated_summary)
    
    # Format and return the scores in a clean structured format
    return {
        "rouge-1": {
            "precision": round(scores["rouge1"].precision, 4),
            "recall": round(scores["rouge1"].recall, 4),
            "f1-score": round(scores["rouge1"].fmeasure, 4)
        },
        "rouge-2": {
            "precision": round(scores["rouge2"].precision, 4),
            "recall": round(scores["rouge2"].recall, 4),
            "f1-score": round(scores["rouge2"].fmeasure, 4)
        },
        "rouge-l": {
            "precision": round(scores["rougeL"].precision, 4),
            "recall": round(scores["rougeL"].recall, 4),
            "f1-score": round(scores["rougeL"].fmeasure, 4)
        }
    }
