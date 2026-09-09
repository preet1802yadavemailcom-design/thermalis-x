import os

observation_schema = """from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ObservationBase(BaseModel):
    source: str
    satellite: str
    instrument: str
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    acq_datetime: datetime
    frp: float = Field(..., ge=0.0)
    brightness: float
    bright_t31: Optional[float] = None
    confidence: str
    scan: float = 1.0
    track: float = 1.0
    daynight: str = "D"
    version: str = "1.0"

class ObservationCreate(ObservationBase):
    pass

class ObservationOut(ObservationBase):
    id: str
    data_quality_status: str
    raw_hash: str
    event_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
"""

with open("backend/app/schemas/observation.py", "w", encoding="utf-8") as f:
    f.write(observation_schema)

event_schema = """from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from backend.app.schemas.observation import ObservationOut

class EventBase(BaseModel):
    id: str
    status: str
    first_seen: datetime
    last_seen: datetime
    duration_hours: float
    observation_count: int
    centroid_lat: float
    centroid_lon: float
    area_ha: float
    max_frp: float
    mean_frp: float
    total_fre_mj: float
    frp_trend: float
    source_class: str
    calibrated_prob: float
    uncertainty: float
    abstained: bool
    priority: str
    priority_score: float
    nearest_facility_id: Optional[str] = None
    distance_to_facility_km: Optional[float] = None
    lineage_type: str = "INITIAL"

class EventSummary(EventBase):
    nearest_facility_name: Optional[str] = None

    class Config:
        from_attributes = True

class EventDetail(EventBase):
    convex_hull_geojson: Optional[str] = None
    raw_probabilities: Optional[Dict[str, float]] = None
    shap_explanation: Optional[Dict[str, Any]] = None
    parent_event_id: Optional[str] = None
    observations: List[ObservationOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
"""

with open("backend/app/schemas/event.py", "w", encoding="utf-8") as f:
    f.write(event_schema)

facility_schema = """from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FacilityBase(BaseModel):
    id: str
    name: str
    facility_type: str
    latitude: float
    longitude: float
    source: str = "OSM"
    source_confidence: float = 0.90
    baseline_median_frp: float = 0.0
    baseline_mad_frp: float = 0.0
    baseline_p90_frp: float = 0.0
    baseline_p99_frp: float = 0.0
    baseline_obs_count: int = 0

class FacilityOut(FacilityBase):
    footprint_geojson: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
"""

with open("backend/app/schemas/facility.py", "w", encoding="utf-8") as f:
    f.write(facility_schema)

alert_schema = """from pydantic import BaseModel
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

    class Config:
        from_attributes = True

class AlertAcknowledgeRequest(BaseModel):
    notes: Optional[str] = None
"""

with open("backend/app/schemas/alert.py", "w", encoding="utf-8") as f:
    f.write(alert_schema)

feedback_schema = """from pydantic import BaseModel
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

    class Config:
        from_attributes = True
"""

with open("backend/app/schemas/feedback.py", "w", encoding="utf-8") as f:
    f.write(feedback_schema)

health_schema = """from pydantic import BaseModel
from typing import Dict, Any

class HealthCheckResponse(BaseModel):
    status: str  # READY, DEGRADED, FAILED
    app_version: str
    demo_mode: bool
    real_data_mode: bool
    components: Dict[str, Any]
"""

with open("backend/app/schemas/health.py", "w", encoding="utf-8") as f:
    f.write(health_schema)

replay_schema = """from pydantic import BaseModel
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
"""

with open("backend/app/schemas/replay.py", "w", encoding="utf-8") as f:
    f.write(replay_schema)

print("Pydantic schemas successfully created.")
