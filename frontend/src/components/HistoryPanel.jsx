export default function HistoryPanel({ history, onSelect, onDelete, onClear }) {
  if (history.length === 0) return null;

  return (
    <div className="history-panel">
      <div className="history-header">
        <h3>Recent searches</h3>
        <button onClick={onClear} className="clear-btn">Clear all</button>
      </div>
      <div className="history-list">
        {history.map((entry) => (
          <div key={entry.id} className="history-entry">
            <button className="history-query" onClick={() => onSelect(entry)}>
              <span className="history-text">{entry.query}</span>
              <span className="history-meta">
                {new Date(entry.timestamp).toLocaleDateString()} ·{" "}
                {entry.metrics?.papers_found ?? "?"} papers
              </span>
            </button>
            <button className="history-delete" onClick={() => onDelete(entry.id)}>×</button>
          </div>
        ))}
      </div>
    </div>
  );
}