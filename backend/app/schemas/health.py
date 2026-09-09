from pydantic import BaseModel
from typing import Dict, Any

class HealthCheckResponse(BaseModel):
    status: str  # READY, DEGRADED, FAILED
    app_version: str
    demo_mode: bool
    real_data_mode: bool
    components: Dict[str, Any]
