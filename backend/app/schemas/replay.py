from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ReplayStep(BaseModel):
    step_index: int
    timestamp: datetime
    action: str
    description: str
    event_id: str
    active_observations_count: int
    current_frp: float
    current_area_ha: float
    current_class: str
    current_priority: str
    alert_triggered: bool

class ReplayCaseOut(BaseModel):
    case_id: str
    title: str
    region: str
    facility_name: str
    description: str
    historical_date: str
    steps_count: int
