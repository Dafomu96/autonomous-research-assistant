import { useState, useCallback } from "react";

const API_BASE = "";
const HISTORY_KEY = "research_history";

const AGENT_LABELS = {
  search: "Searching arXiv papers...",
  analysis: "Analyzing papers with LLM...",
  writer: "Writing research report...",
  critic: "Critic reviewing report...",
};

export function useResearch() {
  const [status, setStatus] = useState("idle"); // idle | loading | streaming | done | error
  const [progress, setProgress] = useState([]);
  const [report, setReport] = useState("");
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState("");

  const getHistory = useCallback(() => {
    try {
      return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    } catch {
      return [];
    }
  }, []);

  const saveToHistory = useCallback((query, reportText, metricsData) => {
    const history = getHistory();
    const entry = {
      id: Date.now(),
      query,
      report: reportText,
      metrics: metricsData,
      timestamp: new Date().toISOString(),
    };
    const updated = [entry, ...history].slice(0, 10); // max 10 entradas
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
    return updated;
  }, [getHistory]);

  const deleteFromHistory = useCallback((id) => {
    const history = getHistory();
    const updated = history.filter((e) => e.id !== id);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
    return updated;
  }, [getHistory]);

  const clearHistory = useCallback(() => {
    localStorage.removeItem(HISTORY_KEY);
    return [];
  }, []);

  const runResearch = useCallback(async (query, maxPapers = 5) => {
    setStatus("streaming");
    setProgress([]);
    setReport("");
    setMetrics(null);
    setError("");

    const startTime = Date.now();

    try {
      const response = await fetch(`${API_BASE}/research/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, max_papers: maxPapers }),
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let finalReport = "";
      let finalMetrics = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith("data:")) {
            try {
              const raw = line.slice(5).trim();
              const parsed = JSON.parse(raw);

              if (parsed.status === "completed") {
                setStatus("done");
                continue;
              }

              if (parsed.error) {
                setError(parsed.error);
                setStatus("error");
                continue;
              }

              const { node, data } = parsed;

              // Construir mensaje de progreso legible
              const label = AGENT_LABELS[node] || `Running ${node}...`;
              const detail = buildDetail(node, data);

              setProgress((prev) => [
                ...prev,
                {
                  id: Date.now() + Math.random(),
                  node,
                  label,
                  detail,
                  timestamp: new Date().toLocaleTimeString(),
                },
              ]);

              // Capturar report preview y métricas
              if (data.report_preview) finalReport = data.report_preview;
              if (data.execution_times) {
                finalMetrics = {
                  total_time_seconds: ((Date.now() - startTime) / 1000).toFixed(2),
                  agent_times: data.execution_times,
                  papers_found: data.papers_found || 0,
                  critic_iterations: data.critic_iteration || 0,
                };
              }
            } catch {
              // línea SSE no parseable, ignorar
            }
          }
        }
      }

      // Si el streaming terminó pero no tenemos report completo, hacemos fetch síncrono
      if (!finalReport || finalReport.endsWith("...")) {
        const res = await fetch(`${API_BASE}/research`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query, max_papers: maxPapers }),
        });
        const data = await res.json();
        finalReport = data.report;
        finalMetrics = data.metrics;
      }

      setReport(finalReport);
      setMetrics(finalMetrics);
      setStatus("done");
      saveToHistory(query, finalReport, finalMetrics);

    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }, [saveToHistory]);

  return {
    status,
    progress,
    report,
    metrics,
    error,
    runResearch,
    getHistory,
    saveToHistory,
    deleteFromHistory,
    clearHistory,
  };
}

function buildDetail(node, data) {
  if (node === "search") return `Found ${data.papers_found ?? "?"} papers`;
  if (node === "analysis") return `Analyzed ${data.analyses_count ?? "?"} papers`;
  if (node === "writer") return data.report_preview ? "Draft ready" : "Writing...";
  if (node === "critic") {
    return data.critic_approved ? "✓ Approved" : `Feedback sent (iter ${data.critic_iteration ?? 1})`;
  }
  return "";
}