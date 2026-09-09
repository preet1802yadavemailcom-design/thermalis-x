from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
