import { useState, useEffect } from "react";
import SearchForm from "./components/SearchForm";
import ProgressTracker from "./components/ProgressTracker";
import ReportViewer from "./components/ReportViewer";
import MetricsPanel from "./components/MetricsPanel";
import HistoryPanel from "./components/HistoryPanel";
import { useResearch } from "./hooks/useResearch";
import "./App.css";

export default function App() {
  const {
    status, progress, report, metrics, error,
    runResearch, getHistory, deleteFromHistory, clearHistory,
  } = useResearch();

  const [history, setHistory] = useState([]);
  const [currentQuery, setCurrentQuery] = useState("");

  useEffect(() => {
    setHistory(getHistory());
  }, []);

  useEffect(() => {
    if (status === "done") setHistory(getHistory());
  }, [status]);

  function handleSubmit(query, maxPapers) {
    setCurrentQuery(query);
    runResearch(query, maxPapers);
  }

  function handleSelectHistory(entry) {
    setCurrentQuery(entry.query);
  }

  function handleDelete(id) {
    setHistory(deleteFromHistory(id));
  }

  function handleClear() {
    setHistory(clearHistory());
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>Autonomous Research Assistant</h1>
          <p className="subtitle">Multi-agent pipeline · LangGraph · Groq Llama 3.3 70B</p>
        </div>
      </header>

      <main className="app-main">
        <div className="left-col">
          <SearchForm
            onSubmit={handleSubmit}
            disabled={status === "streaming" || status === "loading"}
          />

          {error && <div className="error-banner">⚠️ {error}</div>}

          <ProgressTracker progress={progress} status={status} />

          <MetricsPanel metrics={metrics} />

          <HistoryPanel
            history={history}
            onSelect={handleSelectHistory}
            onDelete={handleDelete}
            onClear={handleClear}
          />
        </div>

        <div className="right-col">
          <ReportViewer report={report} query={currentQuery} />
          {!report && status === "idle" && (
            <div className="empty-state">
              <p>Enter a research topic to get started.</p>
              <p className="empty-hint">The pipeline will search arXiv, analyze papers, write a report, and self-critique it.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}