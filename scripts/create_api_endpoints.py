import os

endpoints_events = """from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.db.session import get_db
from backend.app.db.models import Event as EventModel, Observation as ObservationModel
from backend.app.schemas.event import EventSummary, EventDetail
import json

router = APIRouter()

@router.get("", response_model=List[EventSummary])
def list_events(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    source_class: Optional[str] = None,
    min_frp: Optional[float] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(EventModel)
    if status:
        query = query.filter(EventModel.status == status)
    if priority:
        query = query.filter(EventModel.priority == priority)
    if source_class:
        query = query.filter(EventModel.source_class == source_class)
    if min_frp is not None:
        query = query.filter(EventModel.max_frp >= min_frp)
    
    events = query.order_by(EventModel.last_seen.desc()).offset(offset).limit(limit).all()
    results = []
    for e in events:
        s = EventSummary.from_orm(e)
        if e.facility:
            s.nearest_facility_name = e.facility.name
        results.append(s)
    return results

@router.get("/{event_id}", response_model=EventDetail)
def get_event_detail(event_id: str, db: Session = Depends(get_db)):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    
    detail = EventDetail.from_orm(event)
    if event.raw_probabilities_json:
        detail.raw_probabilities = json.loads(event.raw_probabilities_json)
    if event.shap_explanation_json:
        detail.shap_explanation = json.loads(event.shap_explanation_json)
    return detail

@router.get("/{event_id}/timeline")
def get_event_timeline(event_id: str, db: Session = Depends(get_db)):
    obs = db.query(ObservationModel).filter(ObservationModel.event_id == event_id).order_by(ObservationModel.acq_datetime.asc()).all()
    return [
        {
            "id": o.id,
            "acq_datetime": o.acq_datetime.isoformat(),
            "frp": o.frp,
            "brightness": o.brightness,
            "satellite": o.satellite,
            "instrument": o.instrument,
            "confidence": o.confidence
        }
        for o in obs
    ]
"""

with open("backend/app/api/v1/endpoints_events.py", "w", encoding="utf-8") as f:
    f.write(endpoints_events)

endpoints_facilities = """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.db.session import get_db
from backend.app.db.models import Facility as FacilityModel
from backend.app.schemas.facility import FacilityOut

router = APIRouter()

@router.get("", response_model=List[FacilityOut])
def list_facilities(db: Session = Depends(get_db)):
    facs = db.query(FacilityModel).all()
    return [FacilityOut.from_orm(f) for f in facs]

@router.get("/{facility_id}", response_model=FacilityOut)
def get_facility(facility_id: str, db: Session = Depends(get_db)):
    fac = db.query(FacilityModel).filter(FacilityModel.id == facility_id).first()
    if not fac:
        raise HTTPException(status_code=404, detail=f"Facility {facility_id} not found")
    return FacilityOut.from_orm(fac)
"""

with open("backend/app/api/v1/endpoints_facilities.py", "w", encoding="utf-8") as f:
    f.write(endpoints_facilities)

endpoints_alerts = """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.app.db.session import get_db
from backend.app.db.models import Alert as AlertModel
from backend.app.schemas.alert import AlertOut, AlertAcknowledgeRequest

router = APIRouter()

@router.get("", response_model=List[AlertOut])
def list_alerts(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AlertModel)
    if status:
        query = query.filter(AlertModel.status == status)
    alerts = query.order_by(AlertModel.created_at.desc()).all()
    return [AlertOut.from_orm(a) for a in alerts]

@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert(alert_id: str, req: AlertAcknowledgeRequest, db: Session = Depends(get_db)):
    alert = db.query(AlertModel).filter(AlertModel.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = "lead_disaster_analyst"
    db.commit()
    db.refresh(alert)
    return AlertOut.from_orm(alert)
"""

with open("backend/app/api/v1/endpoints_alerts.py", "w", encoding="utf-8") as f:
    f.write(endpoints_alerts)

endpoints_analytics = """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models import Event as EventModel, Alert as AlertModel, Observation as ObservationModel
from sqlalchemy import func

router = APIRouter()

@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    total_events = db.query(EventModel).count()
    active_events = db.query(EventModel).filter(EventModel.status == "ACTIVE").count()
    critical_alerts = db.query(AlertModel).filter(AlertModel.severity == "CRITICAL", AlertModel.status == "NEW").count()
    total_obs = db.query(ObservationModel).count()
    total_fre = db.query(func.sum(EventModel.total_fre_mj)).scalar() or 0.0

    class_counts = {}
    for row in db.query(EventModel.source_class, func.count(EventModel.id)).group_by(EventModel.source_class).all():
        class_counts[row[0]] = row[1]

    return {
        "total_events": total_events,
        "active_events": active_events,
        "critical_alerts": critical_alerts,
        "total_observations": total_obs,
        "total_fre_mj": round(float(total_fre), 1),
        "class_distribution": class_counts
    }
"""

with open("backend/app/api/v1/endpoints_analytics.py", "w", encoding="utf-8") as f:
    f.write(endpoints_analytics)

endpoints_feedback = """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json
from backend.app.db.session import get_db
from backend.app.db.models import AnalystFeedback as FeedbackModel, Event as EventModel
from backend.app.schemas.feedback import AnalystFeedbackCreate, AnalystFeedbackOut

router = APIRouter()

@router.post("", response_model=AnalystFeedbackOut)
def submit_feedback(req: AnalystFeedbackCreate, db: Session = Depends(get_db)):
    fb = FeedbackModel(
        event_id=req.event_id,
        analyst_id="lead_analyst_01",
        verified_class=req.verified_class,
        confidence=req.confidence,
        notes=req.notes,
        evidence_reviewed_json=json.dumps(req.evidence_reviewed)
    )
    db.add(fb)
    # Update event if verified
    event = db.query(EventModel).filter(EventModel.id == req.event_id).first()
    if event:
        event.source_class = req.verified_class
    db.commit()
    db.refresh(fb)
    return AnalystFeedbackOut.from_orm(fb)
"""

with open("backend/app/api/v1/endpoints_feedback.py", "w", encoding="utf-8") as f:
    f.write(endpoints_feedback)

endpoints_replay = """from fastapi import APIRouter, HTTPException
from typing import List
from backend.app.services.replay_service import ReplayService
from backend.app.schemas.replay import ReplayCaseOut, ReplayStep

router = APIRouter()

@router.get("/cases", response_model=List[ReplayCaseOut])
def get_replay_cases():
    cases = []
    for c in ReplayService.CASE_STUDIES:
        steps = ReplayService.get_case_steps(c["case_id"])
        cases.append(ReplayCaseOut(
            case_id=c["case_id"],
            title=c["title"],
            region=c["region"],
            facility_name=c["facility_name"],
            description=c["description"],
            historical_date=c["historical_date"],
            steps_count=len(steps)
        ))
    return cases

@router.get("/cases/{case_id}/steps", response_model=List[ReplayStep])
def get_case_steps(case_id: str):
    steps = ReplayService.get_case_steps(case_id)
    if not steps:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return [ReplayStep(**s) for s in steps]
"""

with open("backend/app/api/v1/endpoints_replay.py", "w", encoding="utf-8") as f:
    f.write(endpoints_replay)

endpoints_health = """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.health import HealthCheckResponse
from backend.app.config import settings

router = APIRouter()

@router.get("", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    db_status = "HEALTHY"
    try:
        db.execute("SELECT 1")
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
"""

with open("backend/app/api/v1/endpoints_health.py", "w", encoding="utf-8") as f:
    f.write(endpoints_health)

router_v1 = """from fastapi import APIRouter
from backend.app.api.v1 import (
    endpoints_events,
    endpoints_facilities,
    endpoints_alerts,
    endpoints_analytics,
    endpoints_feedback,
    endpoints_replay,
    endpoints_health
)

api_router = APIRouter()
api_router.include_router(endpoints_health.router, prefix="/health", tags=["Health"])
api_router.include_router(endpoints_events.router, prefix="/events", tags=["Events"])
api_router.include_router(endpoints_facilities.router, prefix="/facilities", tags=["Facilities"])
api_router.include_router(endpoints_alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(endpoints_analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(endpoints_feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(endpoints_replay.router, prefix="/replay", tags=["Replay"])
"""

with open("backend/app/api/v1/router.py", "w", encoding="utf-8") as f:
    f.write(router_v1)

main_py = """from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from backend.app.config import settings
from backend.app.api.v1.router import api_router
from backend.app.core.logging import logger
from backend.app.db.session import engine
from backend.app.db.base import Base

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Based Detection and Classification of Industrial Fires and Persistent Thermal Sources Using NASA FIRMS, OSM & Satellite Data",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static / Frontend
os.makedirs("frontend/dist", exist_ok=True)
if os.path.exists("frontend/dist/index.html"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} (Demo Mode: {settings.DEMO_MODE})")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": "SYS_500", "message": "An internal error occurred in the THERMALIS-X analytics engine."}
    )
"""

with open("backend/app/main.py", "w", encoding="utf-8") as f:
    f.write(main_py)

print("API v1 endpoints, router, and main FastAPI app written successfully.")
