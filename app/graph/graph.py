from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState
from app.graph.nodes.search import search_agent
from app.graph.nodes.analysis import analysis_agent
from app.graph.nodes.writer import writer_agent
from app.graph.nodes.critic import critic_agent


def should_revise(state: ResearchState) -> str:
    """Edge condicional: ¿el Critic aprueba o manda revisar?"""
    if state.get("critic_approved", False):
        return "approved"
    return "revise"


def build_graph() -> StateGraph:
    graph = StateGraph(ResearchState)

    # Registrar nodos
    graph.add_node("search", search_agent)
    graph.add_node("analysis", analysis_agent)
    graph.add_node("writer", writer_agent)
    graph.add_node("critic", critic_agent)

    # Pipeline fijo
    graph.set_entry_point("search")
    graph.add_edge("search", "analysis")
    graph.add_edge("analysis", "writer")
    graph.add_edge("writer", "critic")

    # Critic como supervisor del Writer (feedback loop)
    graph.add_conditional_edges(
        "critic",
        should_revise,
        {
            "approved": END,
            "revise": "writer",   # vuelve al Writer con feedback embebido en el state
        },
    )

    return graph.compile()


# Singleton — se compila una vez al importar
research_graph = build_graph()