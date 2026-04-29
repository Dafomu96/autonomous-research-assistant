import ReactMarkdown from "react-markdown";

export default function ReportViewer({ report, query }) {
  if (!report) return null;

  function handleCopy() {
    navigator.clipboard.writeText(report);
  }

  function handleDownload() {
    const blob = new Blob([report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `research-${query.slice(0, 30).replace(/\s+/g, "-")}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="report-viewer">
      <div className="report-header">
        <h3>Research report</h3>
        <div className="report-actions">
          <button onClick={handleCopy} className="action-btn">Copy</button>
          <button onClick={handleDownload} className="action-btn">Download .md</button>
        </div>
      </div>
      <div className="report-content">
        <ReactMarkdown>{report}</ReactMarkdown>
      </div>
    </div>
  );
}