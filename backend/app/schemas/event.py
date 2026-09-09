from pydantic import BaseModel, ConfigDict
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
    abnormality_state: str = "NORMAL"
    abnormality_score: float = 0.0
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

    model_config = ConfigDict(from_attributes=True)

class EventDetail(EventBase):
    convex_hull_geojson: Optional[str] = None
    raw_probabilities: Optional[Dict[str, float]] = None
    shap_explanation: Optional[Dict[str, Any]] = None
    conformal_prediction_set: Optional[List[str]] = None
    parent_event_id: Optional[str] = None
    observations: List[ObservationOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
