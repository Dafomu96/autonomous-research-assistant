import time
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.graph.state import ResearchState
from app.core.config import settings
from app.core.logging import logger


CRITIC_SYSTEM_PROMPT = """You are a critical editor evaluating a research report.

Evaluate the report on these dimensions (score 1-5 each):
1. Completeness — does it address the research query fully?
2. Accuracy — are claims grounded in the provided analyses?
3. Structure — is it well-organized and readable?
4. Depth — does it go beyond surface-level summary?

Respond ONLY in this exact format (no other text):
APPROVED: true/false
SCORE: X/20
FEEDBACK: [if not approved, specific actionable improvements needed. If approved, write "None."]

Approve if total score >= 15/20 AND all dimensions >= 3."""


def critic_agent(state: ResearchState) -> dict:
    """Evalúa el informe y decide si aprobarlo o pedir mejoras."""
    start = time.time()
    iteration = state.get("critic_iteration", 0)

    logger.info("critic_agent.start", iteration=iteration)

    # Forzar aprobación si alcanzamos el límite de iteraciones
    if iteration >= settings.max_critic_iterations:
        logger.warning(
            "critic_agent.max_iterations_reached",
            iteration=iteration,
        )
        return {
            "critic_approved": True,
            "critic_feedback": "Max iterations reached — publishing as-is.",
            "critic_iteration": iteration,
            "execution_times": [{"agent": "critic_forced_approve", "seconds": 0}],
        }

    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0.0,  # determinista para el critic
    )

    messages = [
        SystemMessage(content=CRITIC_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Research query: {state['query']}\n\n"
                f"Report to evaluate:\n{state['report_draft']}"
            )
        ),
    ]

    response = llm.invoke(messages)
    content = response.content.strip()

    # Parse respuesta estructurada
    approved = False
    feedback = ""
    try:
        lines = {
            line.split(":")[0].strip(): ":".join(line.split(":")[1:]).strip()
            for line in content.split("\n")
            if ":" in line
        }
        approved = lines.get("APPROVED", "false").lower() == "true"
        feedback = lines.get("FEEDBACK", content)
    except Exception:
        logger.warning("critic_agent.parse_error", raw_response=content)
        approved = False
        feedback = content

    elapsed = round(time.time() - start, 2)
    logger.info(
        "critic_agent.done",
        approved=approved,
        iteration=iteration,
        elapsed_seconds=elapsed,
    )

    return {
        "critic_approved": approved,
        "critic_feedback": feedback if not approved else "",
        "critic_iteration": iteration + 1,
        "execution_times": [{"agent": f"critic_iter_{iteration}", "seconds": elapsed}],
    }