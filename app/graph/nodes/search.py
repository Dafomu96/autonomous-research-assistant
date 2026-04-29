import arxiv
import time
from app.graph.state import ResearchState, PaperInfo
from app.core.config import settings
from app.core.logging import logger


def search_agent(state: ResearchState) -> dict:
    """Busca papers relevantes en arXiv dado el query del usuario."""
    start = time.time()
    query = state["query"]

    logger.info("search_agent.start", query=query, max_papers=settings.max_papers)

    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=settings.max_papers,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        papers: list[PaperInfo] = []
        for result in client.results(search):
            papers.append(
                PaperInfo(
                    title=result.title,
                    authors=[a.name for a in result.authors[:3]],
                    summary=result.summary[:800],  # truncar para no saturar contexto
                    url=result.entry_id,
                    published=result.published.strftime("%Y-%m-%d"),
                )
            )

        elapsed = round(time.time() - start, 2)
        logger.info(
            "search_agent.done",
            papers_found=len(papers),
            elapsed_seconds=elapsed,
        )

        return {
            "papers": papers,
            "total_papers_found": len(papers),
            "execution_times": [{"agent": "search", "seconds": elapsed}],
        }

    except Exception as e:
        logger.error("search_agent.error", error=str(e))
        raise