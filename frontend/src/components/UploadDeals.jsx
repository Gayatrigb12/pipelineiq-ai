import { useRef, useState } from "react";
import { uploadDeals } from "../api/api";

const STATUS = { IDLE: "idle", LOADING: "loading", SUCCESS: "success", ERROR: "error" };

export default function UploadDeals() {
  const [status, setStatus] = useState(STATUS.IDLE);
  const [message, setMessage] = useState("");
  const [fileName, setFileName] = useState("");
  const [preview, setPreview] = useState(null);
  const fileRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;
    if (!file.name.endsWith(".json")) {
      setStatus(STATUS.ERROR);
      setMessage("Only .json files are accepted.");
      return;
    }
    setFileName(file.name);
    setStatus(STATUS.IDLE);
    setMessage("");

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const parsed = JSON.parse(e.target.result);
        // Accept bare array or { deals: [...] }
        const deals = Array.isArray(parsed) ? parsed : parsed.deals;
        if (!Array.isArray(deals) || deals.length === 0) {
          setStatus(STATUS.ERROR);
          setMessage("JSON must contain a non-empty array of deals.");
          return;
        }
        setPreview(deals);
      } catch {
        setStatus(STATUS.ERROR);
        setMessage("Invalid JSON — could not parse file.");
      }
    };
    reader.readAsText(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFile(e.dataTransfer.files[0]);
  };

  const handleSubmit = async () => {
    if (!preview) return;
    setStatus(STATUS.LOADING);
    setMessage("");
    try {
      const res = await uploadDeals(preview);
      setStatus(STATUS.SUCCESS);
      setMessage(
        res.message || `${res.deals_ingested} deal(s) ingested successfully.`
      );
      setPreview(null);
      setFileName("");
    } catch (err) {
      setStatus(STATUS.ERROR);
      setMessage(err.message);
    }
  };

  const reset = () => {
    setStatus(STATUS.IDLE);
    setMessage("");
    setFileName("");
    setPreview(null);
    if (fileRef.current) fileRef.current.value = "";
  };

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Upload Deals</h1>
          <p className="page-subtitle">
            Upload a JSON file to embed your deals into the AI knowledge base.
          </p>
        </div>
      </header>

      {/* Drop zone */}
      <div
        className={"drop-zone" + (fileName ? " drop-zone--filled" : "")}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileRef.current?.click()}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".json"
          className="drop-zone-input"
          onChange={(e) => handleFile(e.target.files[0])}
        />
        <div className="drop-zone-icon">📂</div>
        {fileName ? (
          <p className="drop-zone-filename">{fileName}</p>
        ) : (
          <>
            <p className="drop-zone-label">Drop your JSON file here</p>
            <p className="drop-zone-hint">or click to browse</p>
          </>
        )}
      </div>

      {/* Expected format hint */}
      <details className="format-hint">
        <summary>Expected JSON format</summary>
        <pre className="format-hint-code">{`[
  {
    "deal_name": "Acme Enterprise Q4",
    "company": "Acme Corp",
    "value": 150000,
    "stage": "negotiation",
    "owner": "Jane Smith",
    "last_activity_date": "2024-11-15",
    "lead_source": "inbound",
    "industry": "technology",
    "days_in_stage": 14,
    "notes": "Champion is VP of Eng."
  }
]`}</pre>
      </details>

      {/* Preview */}
      {preview && (
        <div className="preview-box">
          <p className="preview-count">
            ✅ {preview.length} deal{preview.length !== 1 ? "s" : ""} ready to upload
          </p>
          <p className="preview-sample">
            First deal: <strong>{preview[0]?.deal_name || "—"}</strong> /{" "}
            {preview[0]?.company || "—"}
          </p>
        </div>
      )}

      {/* Feedback */}
      {status === STATUS.SUCCESS && (
        <div className="alert alert--success">{message}</div>
      )}
      {status === STATUS.ERROR && (
        <div className="alert alert--error">{message}</div>
      )}

      {/* Actions */}
      <div className="upload-actions">
        <button
          className="btn btn--primary"
          onClick={handleSubmit}
          disabled={!preview || status === STATUS.LOADING}
        >
          {status === STATUS.LOADING ? "Uploading…" : "Upload Deals"}
        </button>
        {(fileName || status !== STATUS.IDLE) && (
          <button className="btn btn--ghost" onClick={reset}>
            Reset
          </button>
        )}
      </div>
    </div>
  );
}