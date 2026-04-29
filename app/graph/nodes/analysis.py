import time
import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.graph.state import ResearchState, PaperAnalysis
from app.core.config import settings
from app.core.logging import logger


ANALYSIS_SYSTEM_PROMPT = """You are a research analyst. For each paper provided, extract:
1. key_findings: 3-5 bullet points of the most important findings
2. methodology: brief description of methods used (1-2 sentences)
3. relevance_score: integer 1-10 indicating relevance to the research query

Respond ONLY with a valid JSON array. No markdown, no preamble.
Format: [{"title": "...", "key_findings": ["..."], "methodology": "...", "relevance_score": 8}]"""


def analysis_agent(state: ResearchState) -> dict:
    """Lee los papers y extrae insights clave usando el LLM."""
    start = time.time()
    papers = state["papers"]
    query = state["query"]

    logger.info("analysis_agent.start", num_papers=len(papers))

    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0.1,
    )

    # Construir el prompt con todos los papers
    papers_text = "\n\n".join(
        f"PAPER {i+1}:\nTitle: {p['title']}\n"
        f"Authors: {', '.join(p['authors'])}\n"
        f"Published: {p['published']}\n"
        f"Abstract: {p['summary']}"
        for i, p in enumerate(papers)
    )

    messages = [
        SystemMessage(content=ANALYSIS_SYSTEM_PROMPT),
        HumanMessage(
            content=f"Research query: {query}\n\nPapers to analyze:\n{papers_text}"
        ),
    ]

    response = llm.invoke(messages)

    # Parse JSON — si falla, construimos análisis básico
    try:
        raw = response.content.strip()
        # Limpiar posibles backticks residuales
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        analyses: list[PaperAnalysis] = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("analysis_agent.json_parse_error", error=str(e))
        # Fallback: análisis básico desde el resumen
        analyses = [
            PaperAnalysis(
                title=p["title"],
                key_findings=[p["summary"][:200]],
                methodology="See original abstract",
                relevance_score=5,
            )
            for p in papers
        ]

    elapsed = round(time.time() - start, 2)
    logger.info("analysis_agent.done", num_analyses=len(analyses), elapsed_seconds=elapsed)

    return {
        "analyses": analyses,
        "execution_times": [{"agent": "analysis", "seconds": elapsed}],
    }