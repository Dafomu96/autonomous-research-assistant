import time
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.graph.state import ResearchState
from app.core.config import settings
from app.core.logging import logger


WRITER_SYSTEM_PROMPT = """You are a scientific writer. Synthesize the research analyses 
into a structured report with these sections:

# Executive Summary
(2-3 sentences capturing the main findings)

# Key Findings
(Bullet points from the analyses, grouped by theme)

# Methodology Overview
(How the papers approached the research question)

# Synthesis & Implications
(What do these findings mean together? What gaps exist?)

# Recommended Papers
(Top 3 papers with brief rationale)

Write in clear, professional English. Be specific, cite paper titles when relevant."""


def writer_agent(state: ResearchState) -> dict:
    """Sintetiza un informe estructurado a partir de los análisis."""
    start = time.time()
    iteration = state.get("critic_iteration", 0)
    feedback = state.get("critic_feedback", "")

    logger.info("writer_agent.start", iteration=iteration, has_feedback=bool(feedback))

    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0.3,
    )

    # Construir contexto de análisis
    analyses_text = "\n\n".join(
        f"Paper: {a['title']}\n"
        f"Key findings: {chr(10).join(f'  - {f}' for f in a['key_findings'])}\n"
        f"Methodology: {a['methodology']}\n"
        f"Relevance: {a['relevance_score']}/10"
        for a in state["analyses"]
    )

    # Incluir feedback del Critic si es iteración > 0
    feedback_section = (
        f"\n\nIMPORTANT — Critic feedback from previous draft (address all points):\n{feedback}"
        if feedback
        else ""
    )

    messages = [
        SystemMessage(content=WRITER_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Research query: {state['query']}\n\n"
                f"Analyses:\n{analyses_text}"
                f"{feedback_section}"
            )
        ),
    ]

    response = llm.invoke(messages)
    elapsed = round(time.time() - start, 2)

    logger.info("writer_agent.done", iteration=iteration, elapsed_seconds=elapsed)

    return {
        "report_draft": response.content,
        "execution_times": [{"agent": f"writer_iter_{iteration}", "seconds": elapsed}],
    }