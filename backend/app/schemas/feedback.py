from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class AnalystFeedbackCreate(BaseModel):
    event_id: str
    verified_class: str
    confidence: float = 1.0
    notes: Optional[str] = None
    evidence_reviewed: List[str] = []

class AnalystFeedbackOut(AnalystFeedbackCreate):
    id: str
    analyst_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
