import time
import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from app.graph.graph import research_graph
from app.graph.state import ResearchState
from app.schemas.research import ResearchRequest, ResearchResponse, ExecutionMetrics
from app.core.config import settings
from app.core.logging import logger

router = APIRouter(prefix="/research", tags=["research"])


def _build_initial_state(request: ResearchRequest) -> ResearchState:
    return ResearchState(
        query=request.query,
        papers=[],
        analyses=[],
        report_draft="",
        critic_approved=False,
        critic_feedback="",
        critic_iteration=0,
        execution_times=[],
        total_papers_found=0,
    )


@router.post("", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """Endpoint síncrono — devuelve el informe completo al terminar."""
    logger.info("api.research.start", query=request.query)
    start = time.time()

    # Override max_papers si viene en el request
    if request.max_papers:
        settings.max_papers = request.max_papers

    try:
        initial_state = _build_initial_state(request)
        final_state: ResearchState = await asyncio.to_thread(
            research_graph.invoke, initial_state
        )
    except Exception as e:
        logger.error("api.research.error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Research pipeline failed: {str(e)}")

    total_time = round(time.time() - start, 2)

    return ResearchResponse(
        query=request.query,
        report=final_state["report_draft"],
        metrics=ExecutionMetrics(
            total_time_seconds=total_time,
            agent_times=final_state["execution_times"],
            papers_found=final_state["total_papers_found"],
            critic_iterations=final_state["critic_iteration"],
        ),
        papers_analyzed=len(final_state["analyses"]),
    )


@router.post("/stream")
async def research_stream(request: ResearchRequest):
    """Endpoint SSE — el cliente ve el progreso en tiempo real."""

    async def event_generator():
        initial_state = _build_initial_state(request)

        try:
            # LangGraph stream mode: emite cada estado intermedio
            for event in research_graph.stream(
                initial_state,
                stream_mode="updates",
            ):
                for node_name, node_output in event.items():
                    # Serializar y emitir el update del nodo
                    payload = {
                        "node": node_name,
                        "data": _serialize_node_output(node_name, node_output),
                    }
                    yield {
                        "event": "node_update",
                        "data": json.dumps(payload),
                    }
                    await asyncio.sleep(0)  # yield control al event loop

            yield {"event": "done", "data": json.dumps({"status": "completed"})}

        except Exception as e:
            logger.error("api.stream.error", error=str(e))
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(event_generator())


def _serialize_node_output(node_name: str, output: dict) -> dict:
    """Limpia el output de cada nodo para SSE — evita serializar objetos no-JSON."""
    serializable = {}
    for key, value in output.items():
        if key == "papers":
            serializable["papers_found"] = len(value)
        elif key == "analyses":
            serializable["analyses_count"] = len(value)
        elif key == "report_draft":
            serializable["report_preview"] = value[:300] + "..." if len(value) > 300 else value
        elif key == "execution_times":
            serializable["execution_times"] = value
        else:
            serializable[key] = value
    return serializable