import { useState } from "react";

export default function SearchForm({ onSubmit, disabled }) {
  const [query, setQuery] = useState("");
  const [maxPapers, setMaxPapers] = useState(5);

  function handleSubmit(e) {
    e.preventDefault();
    if (!query.trim() || disabled) return;
    onSubmit(query.trim(), maxPapers);
  }

  return (
    <form onSubmit={handleSubmit} className="search-form">
      <div className="search-row">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. attention mechanisms in transformers"
          disabled={disabled}
          className="search-input"
        />
        <button type="submit" disabled={disabled || !query.trim()} className="search-btn">
          {disabled ? "Running..." : "Research"}
        </button>
      </div>
      <div className="search-options">
        <label>
          Papers to fetch:
          <select
            value={maxPapers}
            onChange={(e) => setMaxPapers(Number(e.target.value))}
            disabled={disabled}
          >
            {[3, 5, 8, 10].map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </label>
      </div>
    </form>
  );
}