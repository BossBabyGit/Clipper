import { useEffect, useMemo, useState } from "react";
import { API, getClips, getStatus, uploadVideo } from "./api";

const STEP_ICONS = {
  completed: "✅",
  in_progress: "🔄",
  pending: "⏳",
  failed: "⚠️",
};

const STATUS_LABELS = {
  idle: "Idle",
  processing: "Processing",
  completed: "Completed",
  error: "Error",
};

export default function Editor() {
  const [clips, setClips] = useState([]);
  const [processingStatus, setProcessingStatus] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  const steps = processingStatus?.steps ?? [];
  const completedSteps = steps.filter((s) => s.state === "completed").length;
  const progress = steps.length
    ? Math.round((completedSteps / steps.length) * 100)
    : 0;
  const overallState = processingStatus?.state ?? "idle";

  useEffect(() => {
    refreshClips();
    refreshStatus();
  }, []);

  useEffect(() => {
    if (overallState === "processing") {
      const timer = setInterval(() => {
        refreshStatus();
      }, 1500);
      return () => clearInterval(timer);
    }
  }, [overallState]);

  async function refreshClips() {
    try {
      const result = await getClips();
      setClips(result);
    } catch {
      setError("Unable to load clips from the backend.");
    }
  }

  async function refreshStatus() {
    try {
      const status = await getStatus();
      setProcessingStatus(status);
      if (status.state !== "processing") {
        refreshClips();
      }
    } catch {
      setError("Unable to fetch backend status.");
    }
  }

  async function handleUpload(file) {
    if (!file) return;
    setError("");
    setIsUploading(true);
    try {
      await uploadVideo(file);
      await refreshStatus();
    } catch {
      setError("Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  }

  const summaryLine = useMemo(() => {
    if (!processingStatus) return "Waiting for your next upload.";
    if (processingStatus.state === "completed" && processingStatus.summary) {
      return processingStatus.summary;
    }
    if (processingStatus.state === "error") {
      return processingStatus.error || "Pipeline failed.";
    }
    if (processingStatus.state === "processing") {
      return "Crunching through the pipeline…";
    }
    return "Ready whenever you are.";
  }, [processingStatus]);

  return (
    <div className="page">
      <div className="backdrop-ring" aria-hidden />
      <div className="shell">
        <header className="top-bar">
          <div className="brand">
            <span className="logo-mark">C</span>
            <div>
              <p className="eyebrow">Clipper studio</p>
              <h1>Highlights without the heavy lift.</h1>
            </div>
          </div>
          <div className="nav-actions">
            <span className={`pill ${overallState}`}>
              {STATUS_LABELS[overallState] ?? "Status"}
            </span>
            <button className="ghost-button" onClick={refreshStatus}>
              Sync status
            </button>
          </div>
        </header>

        <section className="hero">
          <div>
            <p className="eyebrow">Editless editing</p>
            <h1>
              Create polished highlight reels without leaving your browser{" "}
              <span className="accent">or scrubbing a timeline.</span>
            </h1>
            <p className="lede">
              Drop a VOD, watch the pipeline chew through it, and export the
              moments that matter with captions, previews, and audio baked in.
            </p>
            <div className="hero-cta">
              <button
                className="primary-button"
                type="button"
                onClick={() => document.getElementById("vod-upload")?.click()}
                disabled={isUploading}
              >
                {isUploading ? "Uploading…" : "Upload a VOD"}
              </button>
              <button className="ghost-button" onClick={refreshStatus}>
                Check pipeline
              </button>
            </div>
            <div className="hero-meta">
              <span className={`pill ${overallState}`}>
                {STATUS_LABELS[overallState] ?? "Status"}
              </span>
              <p className="summary-line">{summaryLine}</p>
            </div>
            <div className="hero-stats">
              <div className="stat-card">
                <p className="stat-value">{clips.length}</p>
                <p className="stat-label">Clips detected</p>
              </div>
              <div className="stat-card">
                <p className="stat-value">{steps.length || 0}</p>
                <p className="stat-label">Pipeline steps</p>
              </div>
              <div className="stat-card">
                <p className="stat-value">{progress}%</p>
                <p className="stat-label">Current progress</p>
              </div>
            </div>
          </div>
          <div className="summary-card">
            <p className="eyebrow">Pipeline status</p>
            <p className={`pill ${overallState}`}>
              {STATUS_LABELS[overallState] ?? "Status"}
            </p>
            <p className="summary-line">{summaryLine}</p>
            <div className="status-chip-row">
              <span className="badge">Audio extraction</span>
              <span className="badge">Highlights</span>
              <span className="badge">Subtitles</span>
              <span className="badge">Preview render</span>
            </div>
          </div>
        </section>

        <section className="workspace">
          <div className="panel upload-card">
            <div className="panel-content">
              <div className="upload-header">
                <div>
                  <p className="eyebrow">Step 1</p>
                  <h2>Upload a VOD</h2>
                </div>
                <span className="hint">MP4, up to a few GB</span>
              </div>
              <p className="muted">
                We immediately extract audio, scan for highlight-worthy windows,
                and generate captions so your clip set is ready the moment
                processing wraps.
              </p>

              <label className="upload-area">
                <input
                  id="vod-upload"
                  type="file"
                  accept="video/mp4"
                  onChange={(e) => handleUpload(e.target.files[0])}
                  disabled={isUploading}
                />
                <div>
                  <p className="upload-title">
                    {isUploading ? "Uploading…" : "Drop a VOD or browse files"}
                  </p>
                  <p className="muted">
                    Supported: .mp4 — the backend will show live progress below.
                  </p>
                </div>
                <button className="ghost-button" disabled={isUploading}>
                  Choose file
                </button>
              </label>
              {error && <p className="alert">{error}</p>}
            </div>
          </div>

          <div className="panel status-column">
            <div className="panel-content">
              <div className="status-header">
                <div>
                  <p className="eyebrow">Backend pipeline</p>
                  <h3>Processing timeline</h3>
                </div>
                <span className={`pill ${overallState}`}>
                  {STATUS_LABELS[overallState] ?? "Status"}
                </span>
              </div>
              <div className="progress-track">
                <div
                  className="progress-value"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <ul className="status-list">
                {steps.map((step) => (
                  <li key={step.id} className={`status-item ${step.state}`}>
                    <div className="status-left">
                      <span className="status-icon">
                        {STEP_ICONS[step.state] ?? "•"}
                      </span>
                      <div>
                        <p className="status-title">{step.label}</p>
                        <p className="status-detail">
                          {step.detail || "Waiting to start…"}
                        </p>
                      </div>
                    </div>
                    <span className="badge">{step.state.replace("_", " ")}</span>
                  </li>
                ))}
              </ul>
              {processingStatus?.error && (
                <p className="alert">Error: {processingStatus.error}</p>
              )}
            </div>
          </div>
        </section>

        <section className="clips-section">
          <div className="section-header">
            <div>
              <p className="eyebrow">Step 2</p>
              <h3>Detected clips</h3>
              <p className="muted">
                Refresh after processing to see the latest highlights with links
                to raw footage and subtitles.
              </p>
            </div>
            <button className="ghost-button" onClick={refreshClips}>
              Refresh list
            </button>
          </div>
          <div className="clip-grid">
            {clips.length === 0 && (
              <div className="empty-state">
                <p>No clips yet. Upload a VOD to kick off processing.</p>
              </div>
            )}
            {clips.map((clip) => (
              <article key={clip} className="clip-card">
                <p className="clip-title">{clip}</p>
                <p className="muted">
                  Raw highlight and generated subtitles are available once the
                  pipeline finishes.
                </p>
                <div className="clip-actions">
                  <a href={`${API}/clips/${clip}/raw.mp4`} target="_blank">
                    Raw video
                  </a>
                  <a
                    href={`${API}/clips/${clip}/subtitles.srt`}
                    target="_blank"
                  >
                    Subtitles
                  </a>
                  <a href={`${API}/clips/${clip}/preview.mp4`} target="_blank">
                    Preview (after render)
                  </a>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
