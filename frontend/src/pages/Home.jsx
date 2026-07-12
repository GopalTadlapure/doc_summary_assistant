import React from "react";
import UploadBox from "../components/UploadBox";
import Suggestions from "../components/Suggestions";

function Home() {
  return (
    <div style={styles.outerContainer} className="animate-fade-in">
      <header style={styles.header}>
        <div style={styles.titleContainer}>
          <span style={styles.logoBadge}>AI</span>
          <h1 style={styles.mainTitle}>Document Summary Assistant</h1>
        </div>
        <p style={styles.subtitle}>
          Extract text and generate smart, abstractive summaries using local NLP models. Runs completely offline on your CPU.
        </p>
      </header>

      <main style={styles.mainContent}>
        <div className="dashboard-grid">
          <div style={styles.leftPane}>
            <UploadBox />
          </div>
          <div style={styles.rightPane}>
            <Suggestions />
          </div>
        </div>
      </main>

      <footer style={styles.footer}>
        <p>© 2026 AI Document Summary Assistant. Built with React & local Transformers.</p>
      </footer>
    </div>
  );
}

const styles = {
  outerContainer: {
    maxWidth: "1280px",
    width: "100%",
    margin: "0 auto",
    padding: "40px 24px",
    display: "flex",
    flexDirection: "column",
    gap: "32px",
    flex: 1,
  },
  header: {
    textAlign: "center",
    maxWidth: "700px",
    margin: "0 auto 10px auto",
  },
  titleContainer: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "12px",
    marginBottom: "12px",
  },
  logoBadge: {
    background: "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)",
    color: "#fff",
    fontSize: "13px",
    fontWeight: "700",
    padding: "4px 8px",
    borderRadius: "6px",
    letterSpacing: "0.05em",
    boxShadow: "0 0 15px rgba(99, 102, 241, 0.4)",
  },
  mainTitle: {
    fontSize: "36px",
    fontWeight: "700",
    background: "linear-gradient(90deg, #fff 0%, #cbd5e1 100%)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    letterSpacing: "-0.03em",
  },
  subtitle: {
    fontSize: "15px",
    color: "var(--text-muted)",
    lineHeight: "1.6",
  },
  mainContent: {
    width: "100%",
  },
  leftPane: {
    display: "flex",
    flexDirection: "column",
  },
  rightPane: {
    display: "flex",
    flexDirection: "column",
  },
  footer: {
    textAlign: "center",
    paddingTop: "20px",
    borderTop: "1px solid rgba(255, 255, 255, 0.05)",
    fontSize: "13px",
    color: "var(--text-dark)",
    marginTop: "auto",
  },
};

// Add responsive style logic via Media Queries in CSS
// The grid handles wrapping nicely but on screens smaller than 900px, 
// we will let index.css make this dashboardGrid use flex-direction column.
export default Home;