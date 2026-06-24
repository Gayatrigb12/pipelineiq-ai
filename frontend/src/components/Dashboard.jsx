import { useEffect, useState } from "react";
import { getHealth } from "../api/api";

const STAT_CARDS = [
  {
    label: "Total Deals",
    value: "—",
    sub: "Placeholder — connect your DB",
    accent: "#6366f1",
  },
  {
    label: "Pipeline Value",
    value: "—",
    sub: "Placeholder — connect your DB",
    accent: "#10b981",
  },
  {
    label: "Deals Closed",
    value: "—",
    sub: "Placeholder — connect your DB",
    accent: "#f59e0b",
  },
  {
    label: "Win Rate",
    value: "—",
    sub: "Placeholder — connect your DB",
    accent: "#ef4444",
  },
];

export default function Dashboard() {
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    getHealth()
      .then(() => setApiStatus("online"))
      .catch(() => setApiStatus("offline"));
  }, []);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Revenue Copilot</h1>
          <p className="page-subtitle">
            AI-powered pipeline intelligence for your sales team.
          </p>
        </div>
        <span
          className={
            "status-badge" +
            (apiStatus === "online"
              ? " status-badge--online"
              : apiStatus === "offline"
              ? " status-badge--offline"
              : "")
          }
        >
          <span className="status-dot" />
          {apiStatus === "checking"
            ? "Connecting…"
            : apiStatus === "online"
            ? "API Online"
            : "API Offline"}
        </span>
      </header>

      <section className="stats-grid">
        {STAT_CARDS.map(({ label, value, sub, accent }) => (
          <div className="stat-card" key={label}>
            <div
              className="stat-card-accent"
              style={{ backgroundColor: accent }}
            />
            <p className="stat-label">{label}</p>
            <p className="stat-value">{value}</p>
            <p className="stat-sub">{sub}</p>
          </div>
        ))}
      </section>

      <section className="info-banner">
        <h2 className="info-banner-title">Get started</h2>
        <ol className="info-banner-steps">
          <li>Upload your CRM deals as a JSON file on the <strong>Upload Deals</strong> page.</li>
          <li>The backend embeds each deal into ChromaDB using HuggingFace embeddings.</li>
          <li>Ask natural-language questions on the <strong>AI Chat</strong> page.</li>
        </ol>
      </section>
    </div>
  );
}