import { useState, useEffect } from "react";
import { fetchHealth } from "./api";
import "./App.css";

/** Status badge colours keyed on API `status` field */
const STATUS_STYLES = {
  ok: { color: "#22c55e", label: "● Healthy" },
  error: { color: "#ef4444", label: "● Error" },
  loading: { color: "#a3a3a3", label: "● Connecting…" },
};

export default function App() {
  const [healthData, setHealthData] = useState(null);
  const [uiStatus, setUiStatus] = useState("loading"); // "loading" | "ok" | "error"
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setHealthData(data);
        setUiStatus(data.status === "ok" ? "ok" : "error");
      })
      .catch((err) => {
        setUiStatus("error");
        setErrorMsg(err.message);
      });
  }, []);

  const badge = STATUS_STYLES[uiStatus] ?? STATUS_STYLES.error;

  return (
    <div className="app">
      <header className="hero">
        <div className="hero-content">
          <div className="hero-icon" aria-hidden="true">🚛</div>
          <h1 className="hero-title">Truck Weather Routing</h1>
          <p className="hero-subtitle">
            Weather-aware route planning for safe heavy-haul driving
          </p>
        </div>
      </header>

      <main className="main">
        <section className="card health-card" aria-label="API health status">
          <div className="card-header">
            <span className="card-label">Backend API</span>
            <span
              className="badge"
              style={{ color: badge.color }}
              role="status"
              aria-live="polite"
            >
              {badge.label}
            </span>
          </div>

          {uiStatus === "loading" && (
            <div className="skeleton-block" aria-busy="true" />
          )}

          {uiStatus === "ok" && healthData && (
            <dl className="health-grid">
              <div className="health-row">
                <dt>Status</dt>
                <dd className="value-ok">{healthData.status}</dd>
              </div>
              <div className="health-row">
                <dt>Service</dt>
                <dd>{healthData.service}</dd>
              </div>
              <div className="health-row">
                <dt>Version</dt>
                <dd>{healthData.version}</dd>
              </div>
            </dl>
          )}

          {uiStatus === "error" && (
            <p className="error-msg" role="alert">
              {errorMsg || "Could not reach the backend. Is it running?"}
            </p>
          )}
        </section>

        <section className="card milestone-card">
          <p className="milestone-label">Milestone 1 of 4 complete</p>
          <div className="milestone-track">
            <div className="milestone-fill" />
          </div>
        </section>
      </main>

      <footer className="footer">
        <span>Weather data by Open-Meteo.com</span>
      </footer>
    </div>
  );
}
