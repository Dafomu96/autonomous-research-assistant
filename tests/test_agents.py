import pytest
from unittest.mock import patch, MagicMock
from app.graph.nodes.critic import critic_agent
from app.graph.state import ResearchState


def make_state(**overrides) -> ResearchState:
    base = ResearchState(
        query="attention mechanisms",
        papers=[],
        analyses=[],
        report_draft="This is a test report with sufficient content.",
        critic_approved=False,
        critic_feedback="",
        critic_iteration=0,
        execution_times=[],
        total_papers_found=0,
    )
    return {**base, **overrides}


def test_critic_forces_approve_at_max_iterations():
    """El Critic debe aprobar automáticamente al alcanzar el límite."""
    state = make_state(critic_iteration=3)  # max es 3 por defecto
    result = critic_agent(state)
    assert result["critic_approved"] is True


def test_critic_increments_iteration():
    """Cada llamada al Critic incrementa el contador."""
    mock_response = MagicMock()
    mock_response.content = "APPROVED: false\nSCORE: 10/20\nFEEDBACK: Needs more depth."

    with patch("app.graph.nodes.critic.ChatGroq") as MockLLM:
        MockLLM.return_value.invoke.return_value = mock_response
        state = make_state(critic_iteration=1)
        result = critic_agent(state)
        assert result["critic_iteration"] == 2


def test_critic_parses_approval():
    """El Critic parsea correctamente la respuesta del LLM."""
    mock_response = MagicMock()
    mock_response.content = "APPROVED: true\nSCORE: 17/20\nFEEDBACK: None."

    with patch("app.graph.nodes.critic.ChatGroq") as MockLLM:
        MockLLM.return_value.invoke.return_value = mock_response
        state = make_state(critic_iteration=0)
        result = critic_agent(state)
        assert result["critic_approved"] is True
        assert result["critic_feedback"] == ""