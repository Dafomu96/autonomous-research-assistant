# Autonomous Research Assistant

A multi-agent system (personal project) that autonomously searches academic papers, analyzes them, and synthesizes structured research reports — with a self-critique feedback loop.

Built with **LangGraph**, **Groq (Llama 3.3 70B)**, **FastAPI**, and **React**.

![Pipeline](https://img.shields.io/badge/LangGraph-multi--agent-blue)
![LLM](https://img.shields.io/badge/Groq-Llama%203.3%2070B-orange)
![API](https://img.shields.io/badge/FastAPI-async-green)
![CI](https://github.com/Dafomu96/autonomous-research-assistant/actions/workflows/ci.yml/badge.svg)

---

## Architecture
User Query
│
▼
[Search Agent]    →  Fetches relevant papers from arXiv
│
▼
[Analysis Agent]  →  Extracts key findings, methodology, relevance score
│
▼
[Writer Agent]  ◄────────────────────────┐
│                                     │ feedback loop
▼                                     │ (max 3 iterations)
[Critic Agent]  ─── approved? ──────────►│
│
▼
Final Report

The **Critic Agent** acts as a supervisor of the Writer: if the report scores below 15/20 across four dimensions (completeness, accuracy, structure, depth), it sends structured feedback and the Writer revises. This loop is bounded at 3 iterations to guarantee termination.

---

## Stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph 0.2+ |
| LLM | Groq — Llama 3.3 70B Versatile |
| Paper search | arXiv Python library |
| API | FastAPI + SSE streaming |
| Frontend | React + Vite |
| Containerization | Docker + Docker Compose |
| CI | GitHub Actions |

---

## Features

- **4-agent hybrid pipeline** — fixed sequence with Critic as Writer supervisor
- **Real-time streaming** — SSE endpoint streams each agent's progress to the UI
- **Self-critique loop** — Critic evaluates reports on 4 dimensions, requests revisions if needed
- **Execution metrics** — per-agent timing, papers found, critic iterations
- **Search history** — last 10 queries persisted in localStorage
- **Download reports** — export as `.md` file
- **Structured logging** — JSON logs in production via structlog
- **Pydantic Settings** — environment-based configuration

---

## Project Structure
autonomous-research-assistant/
├── app/
│   ├── api/routes.py          # /research (sync) + /research/stream (SSE)
│   ├── graph/
│   │   ├── state.py           # ResearchState TypedDict (shared memory)
│   │   ├── graph.py           # LangGraph compilation + conditional edges
│   │   └── nodes/             # search / analysis / writer / critic
│   ├── core/
│   │   ├── config.py          # Pydantic Settings
│   │   └── logging.py         # structlog setup
│   └── schemas/research.py    # Request/Response models
├── frontend/
│   └── src/
│       ├── components/        # SearchForm, ProgressTracker, ReportViewer, MetricsPanel, HistoryPanel
│       └── hooks/useResearch.js  # SSE client + localStorage
├── tests/                     # 8 unit tests (agents, graph routing, API)
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── .github/workflows/ci.yml

---

## Quickstart

### Prerequisites
- Python 3.11+
- Node 18+
- [Groq API key](https://console.groq.com) (free)

### Backend

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # add your GROQ_API_KEY
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### Docker

```bash
make build
make run
# API → http://localhost:8000
```

---

## API

### `POST /research`
Synchronous — returns the complete report when the pipeline finishes.

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "attention mechanisms in transformers", "max_papers": 5}'
```

### `POST /research/stream`
Server-Sent Events — streams each agent's update in real time.

```json
// event: node_update
{"node": "search", "data": {"papers_found": 5}}
{"node": "analysis", "data": {"analyses_count": 5}}
{"node": "writer", "data": {"report_preview": "# Executive Summary..."}}
{"node": "critic", "data": {"critic_approved": true, "critic_iteration": 1}}
```

### `GET /health`
```json
{"status": "ok", "version": "1.0.0", "environment": "production"}
```

---

## Key Design Decisions

**`Annotated[list[dict], add]` in ResearchState** — LangGraph's reducer pattern for fields that accumulate across nodes. Without this, the feedback loop would overwrite execution metrics from previous iterations instead of appending them.

**Bounded feedback loop** — the Critic forces approval after `MAX_CRITIC_ITERATIONS` (default: 3) with a warning log. Unbounded loops are the most common failure mode in agentic systems in production.

**`stream_mode="updates"`** — LangGraph emits only the delta of each node, not the full state. More efficient for SSE and demonstrates knowledge of the LangGraph streaming API beyond basic `invoke`.

**Fallback to sync endpoint** — if the SSE stream ends without a complete report (e.g. network interruption), the frontend automatically retries with the synchronous `/research` endpoint.

---

## Tests

```bash
pytest tests/ -v
# 8 passed
```

Covers: Critic approval logic, iteration counter, JSON parsing, graph routing, API endpoints.

---

## Related Projects

- [model-compression-agent](https://gitlab.com/Dafomu96/model-compression-agent) — RAG pipeline with LangGraph for neural network compression queries