export default function MetricsPanel({ metrics }) {
  if (!metrics) return null;

  return (
    <div className="metrics-panel">
      <h3>Execution metrics</h3>
      <div className="metrics-grid">
        <div className="metric-card">
          <span className="metric-value">{metrics.total_time_seconds}s</span>
          <span className="metric-label">Total time</span>
        </div>
        <div className="metric-card">
          <span className="metric-value">{metrics.papers_found}</span>
          <span className="metric-label">Papers found</span>
        </div>
        <div className="metric-card">
          <span className="metric-value">{metrics.critic_iterations}</span>
          <span className="metric-label">Critic iterations</span>
        </div>
        <div className="metric-card">
          <span className="metric-value">{metrics.agent_times?.length ?? 0}</span>
          <span className="metric-label">Agent calls</span>
        </div>
      </div>
      {metrics.agent_times?.length > 0 && (
        <div className="agent-times">
          {metrics.agent_times.map((t, i) => (
            <div key={i} className="agent-time-row">
              <span className="agent-name">{t.agent}</span>
              <div className="time-bar-wrapper">
                <div
                  className="time-bar"
                  style={{
                    width: `${Math.min(100, (t.seconds / metrics.total_time_seconds) * 100)}%`,
                  }}
                />
              </div>
              <span className="agent-seconds">{t.seconds}s</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}