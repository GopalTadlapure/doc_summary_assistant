import React from "react";
import { jsPDF } from "jspdf";

function SummaryCard({ data }) {
  if (!data) return null;

  const {
    filename,
    summary,
    word_count,
    processing_time,
    extracted_word_count,
    rouge_scores,
  } = data;

  const downloadTXT = () => {
    const header = `AI DOCUMENT SUMMARY\n====================\n`;
    const metadata = `File: ${filename}\nOriginal Length: ${extracted_word_count} words\nSummary Length: ${word_count} words\nProcessing Time: ${processing_time}\n\n`;
    const body = `SUMMARY:\n--------------------\n${summary}\n`;
    
    const element = document.createElement("a");
    const file = new Blob([header + metadata + body], { type: "text/plain;charset=utf-8" });
    element.href = URL.createObjectURL(file);
    element.download = `${filename.replace(/\.[^/.]+$/, "")}_summary.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const downloadPDF = () => {
    const doc = new jsPDF();

    // Setup basic document fonts
    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.setTextColor(30, 41, 59); // Slate-800
    doc.text("AI Document Summary", 20, 25);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(100, 116, 139); // Slate-500
    doc.text(`Source File: ${filename}`, 20, 34);
    doc.text(`Generated On: ${new Date().toLocaleString()}`, 20, 39);
    doc.text(`Metrics: ${word_count} words (summary) | ${extracted_word_count} words (original) | Time: ${processing_time}`, 20, 44);

    // Draw separation line
    doc.setDrawColor(226, 232, 240); // Slate-200
    doc.line(20, 48, 190, 48);

    // Text configuration
    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);
    doc.setTextColor(51, 65, 85); // Slate-700
    
    // Split the summary text so it conforms to standard A4 printing bounds (170mm width)
    const splitText = doc.splitTextToSize(summary, 170);

    let cursorY = 58;
    const pageHeight = doc.internal.pageSize.height;

    splitText.forEach((line) => {
      // Add a page if text overflows
      if (cursorY > pageHeight - 20) {
        doc.addPage();
        cursorY = 25;
      }
      doc.text(line, 20, cursorY);
      cursorY += 6.5; // Line spacing
    });

    // If ROUGE scores exist, write them on a new page (or bottom of page if space permits)
    if (rouge_scores) {
      if (cursorY > pageHeight - 75) {
        doc.addPage();
        cursorY = 25;
      } else {
        cursorY += 10;
        doc.setDrawColor(226, 232, 240);
        doc.line(20, cursorY, 190, cursorY);
        cursorY += 10;
      }

      doc.setFont("helvetica", "bold");
      doc.setFontSize(14);
      doc.setTextColor(30, 41, 59);
      doc.text("ROUGE Evaluation Metrics", 20, cursorY);
      cursorY += 10;

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(71, 85, 105);

      const metrics = ["rouge-1", "rouge-2", "rouge-l"];
      metrics.forEach((metric) => {
        const score = rouge_scores[metric];
        if (score) {
          const formattedMetricName = metric.toUpperCase();
          doc.text(
            `${formattedMetricName}:   F1-Score: ${(score["f1-score"] * 100).toFixed(2)}%  |  Precision: ${(score.precision * 100).toFixed(2)}%  |  Recall: ${(score.recall * 100).toFixed(2)}%`,
            20,
            cursorY
          );
          cursorY += 8;
        }
      });
    }

    doc.save(`${filename.replace(/\.[^/.]+$/, "")}_summary.pdf`);
  };

  return (
    <div style={styles.card} className="glass-panel animate-slide-up">
      <div style={styles.header}>
        <div>
          <h2 style={styles.title}>📑 Summary Generated</h2>
          <span style={styles.filename}>{filename}</span>
        </div>
        <div style={styles.downloadGroup}>
          <button onClick={downloadTXT} className="btn btn-outline" style={styles.btnSmall}>
            💾 Download TXT
          </button>
          <button onClick={downloadPDF} className="btn btn-primary" style={styles.btnSmall}>
            📄 Download PDF
          </button>
        </div>
      </div>

      <div style={styles.metaGrid}>
        <div style={styles.metaItem}>
          <span style={styles.metaLabel}>Processing Time</span>
          <span style={styles.metaValue}>{processing_time}</span>
        </div>
        <div style={styles.metaItem}>
          <span style={styles.metaLabel}>Summary Length</span>
          <span style={styles.metaValue}>{word_count} words</span>
        </div>
        <div style={styles.metaItem}>
          <span style={styles.metaLabel}>Original Length</span>
          <span style={styles.metaValue}>{extracted_word_count} words</span>
        </div>
        <div style={styles.metaItem}>
          <span style={styles.metaLabel}>Compression Ratio</span>
          <span style={styles.metaValue}>
            {extracted_word_count > 0
              ? `${Math.round((1 - word_count / extracted_word_count) * 100)}%`
              : "0%"}
          </span>
        </div>
      </div>

      {rouge_scores && (
        <div style={styles.rougeContainer}>
          <h3 style={styles.sectionTitle}>🎯 ROUGE Performance Scores</h3>
          <div style={styles.rougeGrid}>
            {Object.keys(rouge_scores).map((key) => {
              const f1Percent = Math.round(rouge_scores[key]["f1-score"] * 100);
              const precisionPercent = Math.round(rouge_scores[key].precision * 100);
              const recallPercent = Math.round(rouge_scores[key].recall * 100);
              
              return (
                <div key={key} style={styles.rougeCard}>
                  <div style={styles.rougeCardHeader}>
                    <span style={styles.rougeMetricName}>{key.toUpperCase()}</span>
                    <span style={styles.rougeF1Badge}>F1: {f1Percent}%</span>
                  </div>
                  
                  <div style={styles.rougeMetricRow}>
                    <div style={styles.subMetric}>
                      <span>Precision: {precisionPercent}%</span>
                      <div style={styles.miniBarContainer}>
                        <div style={{ ...styles.miniBar, width: `${precisionPercent}%`, backgroundColor: '#3b82f6' }} />
                      </div>
                    </div>
                    <div style={styles.subMetric}>
                      <span>Recall: {recallPercent}%</span>
                      <div style={styles.miniBarContainer}>
                        <div style={{ ...styles.miniBar, width: `${recallPercent}%`, backgroundColor: '#10b981' }} />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div style={styles.summaryBody}>
        <h3 style={styles.sectionTitle}>Summary Content</h3>
        <p style={styles.summaryText}>{summary}</p>
      </div>
    </div>
  );
}

const styles = {
  card: {
    marginTop: "30px",
    textAlign: "left",
    animationDelay: "0.2s",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    flexWrap: "wrap",
    gap: "16px",
    borderBottom: "1px solid rgba(255,255,255,0.06)",
    paddingBottom: "16px",
    marginBottom: "20px",
  },
  title: {
    fontSize: "20px",
    fontWeight: "600",
  },
  filename: {
    fontSize: "13px",
    color: "var(--text-muted)",
  },
  downloadGroup: {
    display: "flex",
    gap: "10px",
  },
  btnSmall: {
    padding: "8px 16px",
    fontSize: "13px",
  },
  metaGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
    gap: "16px",
    marginBottom: "24px",
  },
  metaItem: {
    background: "rgba(15, 23, 42, 0.3)",
    border: "1px solid rgba(255,255,255,0.03)",
    padding: "12px",
    borderRadius: "8px",
    display: "flex",
    flexDirection: "column",
  },
  metaLabel: {
    fontSize: "12px",
    color: "var(--text-dark)",
    textTransform: "uppercase",
    fontWeight: "500",
    marginBottom: "4px",
  },
  metaValue: {
    fontSize: "16px",
    fontWeight: "600",
    color: "var(--text-main)",
  },
  rougeContainer: {
    marginBottom: "24px",
    padding: "16px",
    background: "rgba(99, 102, 241, 0.05)",
    border: "1px solid rgba(99, 102, 241, 0.15)",
    borderRadius: "10px",
  },
  sectionTitle: {
    fontSize: "15px",
    fontWeight: "600",
    color: "var(--text-main)",
    marginBottom: "12px",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  rougeGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: "12px",
  },
  rougeCard: {
    background: "rgba(15, 23, 42, 0.4)",
    border: "1px solid rgba(255,255,255,0.05)",
    borderRadius: "8px",
    padding: "12px",
  },
  rougeCardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "8px",
    borderBottom: "1px solid rgba(255,255,255,0.04)",
    paddingBottom: "6px",
  },
  rougeMetricName: {
    fontWeight: "600",
    fontSize: "12px",
    color: "var(--text-muted)",
  },
  rougeF1Badge: {
    fontSize: "12px",
    fontWeight: "700",
    color: "#a855f7",
  },
  rougeMetricRow: {
    display: "flex",
    flexDirection: "column",
    gap: "6px",
  },
  subMetric: {
    fontSize: "11px",
    color: "var(--text-dark)",
    display: "flex",
    flexDirection: "column",
    gap: "2px",
  },
  miniBarContainer: {
    height: "4px",
    backgroundColor: "rgba(255, 255, 255, 0.05)",
    borderRadius: "2px",
    width: "100%",
    overflow: "hidden",
  },
  miniBar: {
    height: "100%",
    borderRadius: "2px",
  },
  summaryBody: {
    background: "rgba(15, 23, 42, 0.2)",
    border: "1px solid rgba(255,255,255,0.04)",
    padding: "20px",
    borderRadius: "10px",
  },
  summaryText: {
    fontSize: "15px",
    lineHeight: "1.7",
    color: "#cbd5e1",
    whiteSpace: "pre-wrap",
  },
};

export default SummaryCard;
