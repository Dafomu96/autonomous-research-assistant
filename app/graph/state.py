from typing import TypedDict, Annotated
from operator import add


class PaperInfo(TypedDict):
    title: str
    authors: list[str]
    summary: str
    url: str
    published: str


class PaperAnalysis(TypedDict):
    title: str
    key_findings: list[str]
    methodology: str
    relevance_score: int  # 1-10


class ResearchState(TypedDict):
    # Input
    query: str

    # Search Agent output
    papers: list[PaperInfo]

    # Analysis Agent output
    analyses: list[PaperAnalysis]

    # Writer Agent output
    report_draft: str

    # Critic Agent output
    critic_approved: bool
    critic_feedback: str
    critic_iteration: int  # contador de iteraciones

    # Metadata para métricas
    execution_times: Annotated[list[dict], add]  # acumula con add reducer
    total_papers_found: int