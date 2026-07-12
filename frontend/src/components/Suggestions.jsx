import React from "react";

function Suggestions() {
  return (
    <div style={styles.container} className="glass-panel animate-slide-up">
      <h3 style={styles.title}>💡 How It Works</h3>
      
      <div style={styles.item}>
        <div style={styles.bullet}>1</div>
        <div>
          <strong style={styles.strong}>OCR Pipeline Enabled</strong>
          <p style={styles.text}>
            Upload scanned PDFs or images (PNG, JPG). The assistant auto-detects if there's no digital text and invokes local Tesseract OCR.
          </p>
        </div>
      </div>

      <div style={styles.item}>
        <div style={styles.bullet}>2</div>
        <div>
          <strong style={styles.strong}>Local Sentence Chunker</strong>
          <p style={styles.text}>
            Large files are cleaned and segmented into sentence-aligned blocks of 300 words. This avoids token-overflow issues in the model.
          </p>
        </div>
      </div>

      <div style={styles.item}>
        <div style={styles.bullet}>3</div>
        <div>
          <strong style={styles.strong}>T5-Small Transformer</strong>
          <p style={styles.text}>
            An abstractive local summarizer model running entirely offline on your computer. Output length maps to: Short (~80t), Medium (~150t), or Long (~250t).
          </p>
        </div>
      </div>

      <div style={styles.item}>
        <div style={styles.bullet}>4</div>
        <div>
          <strong style={styles.strong}>ROUGE Score Checker</strong>
          <p style={styles.text}>
            Input a reference summary to calculate precision, recall, and F1 scores across ROUGE-1, ROUGE-2, and ROUGE-L.
          </p>
        </div>
      </div>
      
      <div style={styles.tipCard}>
        <span style={styles.tipTag}>PRO TIP</span>
        <p style={styles.tipText}>
          If Tesseract OCR or Poppler is not installed, digital PDF text extraction will still work, but image/scanned PDF uploads will throw a setup notification.
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    height: "fit-content",
    textAlign: "left",
  },
  title: {
    fontSize: "18px",
    fontWeight: "600",
    marginBottom: "20px",
    borderBottom: "1px solid rgba(255,255,255,0.06)",
    paddingBottom: "10px",
  },
  item: {
    display: "flex",
    gap: "14px",
    marginBottom: "18px",
    alignItems: "flex-start",
  },
  bullet: {
    width: "24px",
    height: "24px",
    borderRadius: "50%",
    background: "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "12px",
    fontWeight: "700",
    flexShrink: 0,
    marginTop: "2px",
    boxShadow: "0 2px 6px rgba(99, 102, 241, 0.3)",
  },
  strong: {
    fontSize: "14px",
    color: "var(--text-main)",
    display: "block",
    marginBottom: "4px",
  },
  text: {
    fontSize: "13px",
    color: "var(--text-muted)",
    lineHeight: "1.5",
  },
  tipCard: {
    marginTop: "20px",
    background: "rgba(168, 85, 247, 0.04)",
    border: "1px dashed rgba(168, 85, 247, 0.2)",
    borderRadius: "8px",
    padding: "12px",
  },
  tipTag: {
    fontSize: "10px",
    fontWeight: "700",
    color: "#a855f7",
    background: "rgba(168, 85, 247, 0.15)",
    padding: "2px 6px",
    borderRadius: "4px",
    display: "inline-block",
    marginBottom: "6px",
  },
  tipText: {
    fontSize: "12px",
    color: "var(--text-muted)",
    lineHeight: "1.4",
  },
};

export default Suggestions;
