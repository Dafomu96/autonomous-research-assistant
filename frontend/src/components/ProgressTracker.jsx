const NODE_ICONS = {
  search: "🔍",
  analysis: "🧠",
  writer: "✍️",
  critic: "🔎",
};

export default function ProgressTracker({ progress, status }) {
  if (progress.length === 0 && status === "idle") return null;

  return (
    <div className="progress-tracker">
      <h3>Pipeline progress</h3>
      <div className="progress-steps">
        {progress.map((step) => (
          <div key={step.id} className="progress-step">
            <span className="step-icon">{NODE_ICONS[step.node] || "⚙️"}</span>
            <div className="step-content">
              <span className="step-label">{step.label}</span>
              {step.detail && <span className="step-detail">{step.detail}</span>}
            </div>
            <span className="step-time">{step.timestamp}</span>
          </div>
        ))}
        {status === "streaming" && (
          <div className="progress-step loading">
            <span className="step-icon spinning">⚙️</span>
            <span className="step-label">Processing...</span>
          </div>
        )}
        {status === "done" && (
          <div className="progress-step done">
            <span className="step-icon">✅</span>
            <span className="step-label">Pipeline complete</span>
          </div>
        )}
      </div>
    </div>
  );
}