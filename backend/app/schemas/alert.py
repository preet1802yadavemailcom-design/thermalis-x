from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class AlertBase(BaseModel):
    event_id: str
    severity: str
    title: str
    description: str
    priority_score: float
    facility_name: Optional[str] = None
    recommended_action: str

class AlertOut(AlertBase):
    id: str
    status: str
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AlertAcknowledgeRequest(BaseModel):
    notes: Optional[str] = None
