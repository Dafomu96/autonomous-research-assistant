import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
from app.main import app


MOCK_FINAL_STATE = {
    "query": "transformers",
    "papers": [{"title": "T", "authors": [], "summary": "", "url": "", "published": ""}],
    "analyses": [{"title": "T", "key_findings": [], "methodology": "", "relevance_score": 8}],
    "report_draft": "# Report\n\nContent here.",
    "critic_approved": True,
    "critic_feedback": "",
    "critic_iteration": 1,
    "execution_times": [{"agent": "search", "seconds": 1.2}],
    "total_papers_found": 1,
}


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_research_endpoint():
    with patch("app.api.routes.research_graph.invoke", return_value=MOCK_FINAL_STATE):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/research", json={"query": "transformers"})
    assert response.status_code == 200
    data = response.json()
    assert "report" in data
    assert data["metrics"]["papers_found"] == 1