import { useState } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";
import Loader from "./Loader";
import SummaryCard from "./SummaryCard";

function UploadBox() {
  const [file, setFile] = useState(null);
  const [summaryLength, setSummaryLength] = useState("short");
  const [referenceSummary, setReferenceSummary] = useState("");
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "application/pdf": [".pdf"],
      "image/*": [".png", ".jpg", ".jpeg"],
    },
    multiple: false,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setFile(acceptedFiles[0]);
        setSummaryData(null);
        setUploadProgress(0);
      }
    },
  });

  const handleGenerate = async () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    setLoading(true);
    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("summaryLength", summaryLength);
    if (referenceSummary.trim()) {
      formData.append("referenceSummary", referenceSummary.trim());
    }

    try {
      const response = await axios.post(
  "https://docsummaryassistant-production.up.railway.app/upload",
  formData,
  {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percentCompleted = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              setUploadProgress(percentCompleted);
              if (percentCompleted >= 100) {
                setUploading(false); // Finished uploading, now processing
              }
            }
          },
        }
      );

      setUploading(false);

      if (response.data.success) {
        setSummaryData(response.data);
      } else {
        alert(response.data.message || "Pipeline error");
      }
    } catch (error) {
      console.error(error);
      setUploading(false);
      const errorMsg = error.response?.data?.message || "Upload and summarization failed. Please check backend logs.";
      alert(errorMsg);
    }

    setLoading(false);
  };

  const clearFile = () => {
    setFile(null);
    setSummaryData(null);
    setReferenceSummary("");
  };

  return (
    <div style={styles.container}>
      {loading && (
        <Loader 
          message={uploading ? "Uploading document to server..." : "Running AI pipeline (extracting & summarizing)..."} 
          progress={uploading ? uploadProgress : null} 
        />
      )}

      <div className="controls-grid">
        <div style={styles.leftColumn}>
          {/* Dropzone Panel */}
          <div
            {...getRootProps()}
            style={{
              ...styles.dropzone,
              borderColor: isDragActive ? "var(--primary-color)" : "var(--panel-border)",
              background: isDragActive ? "rgba(99, 102, 241, 0.05)" : "rgba(30, 41, 59, 0.2)",
            }}
          >
            <input {...getInputProps()} />
            <div style={styles.dropzoneContent}>
              <span style={styles.icon}>📁</span>
              <h3 style={styles.dropzoneTitle}>
                {isDragActive ? "Drop the file here..." : "Drag & drop your file"}
              </h3>
              <p style={styles.dropzoneText}>or click to browse from folder</p>
              <span style={styles.fileSupport}>Supported formats: PDF, PNG, JPG</span>
            </div>
          </div>

          {/* Selected File Details */}
          {file && (
            <div style={styles.filePanel} className="glass-panel animate-fade-in">
              <div style={styles.fileDetails}>
                <span style={styles.fileIcon}>📄</span>
                <div style={styles.fileInfo}>
                  <div style={styles.fileName}>{file.name}</div>
                  <div style={styles.fileSize}>
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                </div>
              </div>
              <button onClick={clearFile} style={styles.clearBtn}>
                ✕
              </button>
            </div>
          )}
        </div>

        <div style={styles.rightColumn} className="glass-panel">
          {/* Summary Length Config */}
          <div style={styles.section}>
            <h4 style={styles.sectionLabel}>Target Summary Length</h4>
            <div className="radio-group">
              {["short", "medium", "long"].map((len) => (
                <label
                  key={len}
                  className={`radio-label ${summaryLength === len ? "checked" : ""}`}
                >
                  <input
                    type="radio"
                    name="summaryLength"
                    value={len}
                    checked={summaryLength === len}
                    onChange={(e) => setSummaryLength(e.target.value)}
                  />
                  {len.charAt(0).toUpperCase() + len.slice(1)}
                </label>
              ))}
            </div>
          </div>

          {/* Optional ROUGE Validation Ref Summary */}
          <div style={styles.section}>
            <h4 style={styles.sectionLabel}>
              Reference Summary <span style={styles.optional}>(Optional - for ROUGE evaluation)</span>
            </h4>
            <textarea
              style={styles.textarea}
              placeholder="Paste reference summary text here to evaluate ROUGE precision, recall, and F1 metrics..."
              value={referenceSummary}
              onChange={(e) => setReferenceSummary(e.target.value)}
              rows={4}
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={!file || loading}
            className="btn btn-primary"
            style={styles.generateBtn}
          >
            {loading ? "Processing Pipeline..." : "✨ Generate Summary"}
          </button>
        </div>
      </div>

      {/* Summarization Results Display */}
      {summaryData && <SummaryCard data={summaryData} />}
    </div>
  );
}

const styles = {
  container: {
    width: "100%",
  },
  leftColumn: {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },
  rightColumn: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    gap: "20px",
  },
  dropzone: {
    flex: 1,
    border: "2px dashed var(--panel-border)",
    borderRadius: "var(--border-radius)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    transition: "var(--transition)",
    padding: "40px 20px",
    minHeight: "220px",
  },
  dropzoneContent: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    textAlign: "center",
  },
  icon: {
    fontSize: "48px",
    marginBottom: "16px",
    display: "block",
  },
  dropzoneTitle: {
    fontSize: "16px",
    fontWeight: "600",
    marginBottom: "4px",
  },
  dropzoneText: {
    fontSize: "14px",
    color: "var(--text-muted)",
    marginBottom: "12px",
  },
  fileSupport: {
    fontSize: "11px",
    color: "var(--text-dark)",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  filePanel: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "16px",
  },
  fileDetails: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
  },
  fileIcon: {
    fontSize: "24px",
  },
  fileInfo: {
    display: "flex",
    flexDirection: "column",
  },
  fileName: {
    fontSize: "14px",
    fontWeight: "500",
    color: "var(--text-main)",
    maxWidth: "260px",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  fileSize: {
    fontSize: "12px",
    color: "var(--text-dark)",
  },
  clearBtn: {
    background: "transparent",
    border: "none",
    color: "var(--text-dark)",
    cursor: "pointer",
    fontSize: "16px",
    transition: "var(--transition)",
    padding: "4px",
  },
  section: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  sectionLabel: {
    fontSize: "13px",
    fontWeight: "600",
    color: "var(--text-muted)",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  optional: {
    color: "var(--text-dark)",
    fontSize: "11px",
    textTransform: "none",
    fontWeight: "normal",
  },
  textarea: {
    resize: "none",
    lineHeight: "1.5",
  },
  generateBtn: {
    width: "100%",
    height: "46px",
  },
};

export default UploadBox;