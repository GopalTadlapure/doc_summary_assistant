import React from "react";

function Loader({ message = "Processing document...", progress = null }) {
  return (
    <div style={styles.overlay} className="animate-fade-in">
      <div style={styles.container} className="glass-panel">
        <div style={styles.spinnerContainer}>
          <div style={styles.spinner}></div>
          <div style={styles.innerGlow}></div>
        </div>
        <h3 style={styles.message}>{message}</h3>
        {progress !== null && (
          <div style={styles.progressContainer}>
            <div style={styles.progressBarWrapper}>
              <div 
                style={{ ...styles.progressBar, width: `${progress}%` }}
              ></div>
            </div>
            <span style={styles.progressText}>{progress}% uploaded</span>
          </div>
        )}
        <p style={styles.subtext}>
          Running Tesseract OCR & local T5 Summarization. This runs entirely on your device and may take a few moments.
        </p>
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(2, 6, 23, 0.8)",
    backdropFilter: "blur(8px)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
  },
  container: {
    maxWidth: "400px",
    width: "90%",
    textAlign: "center",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "40px 30px",
  },
  spinnerContainer: {
    position: "relative",
    width: "80px",
    height: "80px",
    marginBottom: "24px",
  },
  spinner: {
    width: "100%",
    height: "100%",
    borderRadius: "50%",
    border: "4px solid rgba(99, 102, 241, 0.1)",
    borderTopColor: "#6366f1",
    borderRightColor: "#a855f7",
    animation: "spin-slow 1.2s linear infinite",
  },
  innerGlow: {
    position: "absolute",
    top: "10px",
    left: "10px",
    right: "10px",
    bottom: "10px",
    borderRadius: "50%",
    background: "radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%)",
  },
  message: {
    fontSize: "18px",
    fontWeight: "600",
    marginBottom: "12px",
    color: "#fff",
  },
  progressContainer: {
    width: "100%",
    margin: "15px 0",
  },
  progressBarWrapper: {
    width: "100%",
    height: "6px",
    backgroundColor: "rgba(255, 255, 255, 0.05)",
    borderRadius: "3px",
    overflow: "hidden",
    marginBottom: "8px",
  },
  progressBar: {
    height: "100%",
    background: "linear-gradient(90deg, #6366f1 0%, #a855f7 100%)",
    borderRadius: "3px",
    transition: "width 0.2s ease-out",
  },
  progressText: {
    fontSize: "12px",
    color: "#a855f7",
    fontWeight: "500",
  },
  subtext: {
    fontSize: "12px",
    color: "#64748b",
    marginTop: "8px",
    lineHeight: "1.6",
  },
};

export default Loader;
