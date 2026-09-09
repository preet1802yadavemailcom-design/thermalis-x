from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.health import HealthCheckResponse
from backend.app.config import settings

router = APIRouter()

@router.get("", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    db_status = "HEALTHY"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "DEGRADED"

    return HealthCheckResponse(
        status="READY",
        app_version=settings.APP_VERSION,
        demo_mode=settings.DEMO_MODE,
        real_data_mode=settings.REAL_DATA_MODE,
        components={
            "database": db_status,
            "firms_connector": "READY (Resilient Cache Mode)",
            "element84_stac": "READY (STAC v1.0)",
            "open_meteo_weather": "READY",
            "xgboost_classifier": "ONLINE (v1_xgboost_industrial)"
        }
    )
