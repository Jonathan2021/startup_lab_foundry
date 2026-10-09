"""Common score summary for idea and independent venture presentation."""

from pydantic import BaseModel, ConfigDict, Field


class ScoreSummary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")
    id: str
    scorecard_id: str
    total: float | None = Field(ge=0, le=100)
    confidence: str
    coverage: int = Field(ge=0)
    required: int = Field(ge=1)
    label: str
    rationale: str | None
    author: str | None
    created_at: str
