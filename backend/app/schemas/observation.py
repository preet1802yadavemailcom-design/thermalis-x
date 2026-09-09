from pydantic import BaseModel, Field, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
