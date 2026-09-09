from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class AnalystFeedbackCreate(BaseModel):
    event_id: str
    verified_class: str
    confidence: float = 1.0
    notes: Optional[str] = None
    evidence_reviewed: List[str] = []
    analyst_id: Optional[str] = "lead_analyst_01"

class AnalystFeedbackOut(BaseModel):
    id: str
    event_id: str
    analyst_id: str
    verified_class: str
    confidence: float
    notes: Optional[str] = None
    evidence_reviewed: List[str] = []
    status: str = "APPROVED"
    supervisor_id: Optional[str] = None
    supervisor_notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SupervisorApprovalRequest(BaseModel):
    approved: bool
    supervisor_id: str
    supervisor_notes: Optional[str] = None
