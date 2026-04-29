from pydantic import BaseModel, Field
from typing import Optional


class ResearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        max_length=300,
        examples=["transformer attention mechanisms in NLP"],
    )
    max_papers: Optional[int] = Field(default=None, ge=1, le=20)


class ExecutionMetrics(BaseModel):
    total_time_seconds: float
    agent_times: list[dict]
    papers_found: int
    critic_iterations: int


class ResearchResponse(BaseModel):
    query: str
    report: str
    metrics: ExecutionMetrics
    papers_analyzed: int