from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.db.session import get_db
from backend.app.db.models import Event as EventModel, Observation as ObservationModel
from backend.app.schemas.event import EventSummary, EventDetail
from backend.app.services.risk_engine import RiskPriorityEngine
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
        s = EventSummary.model_validate(e)
        if e.facility:
            s.nearest_facility_name = e.facility.name
        results.append(s)
    return results

@router.get("/{event_id}", response_model=EventDetail)
def get_event_detail(event_id: str, db: Session = Depends(get_db)):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    
    detail = EventDetail.model_validate(event)
    if event.raw_probabilities_json:
        detail.raw_probabilities = json.loads(event.raw_probabilities_json)
    if event.shap_explanation_json:
        detail.shap_explanation = json.loads(event.shap_explanation_json)
    if event.conformal_set_json:
        detail.conformal_prediction_set = json.loads(event.conformal_set_json)
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

@router.get("/{event_id}/response-plan")
def get_event_response_plan(event_id: str, db: Session = Depends(get_db)):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    fac_type = event.facility.facility_type if event.facility else "none"
    plan = RiskPriorityEngine.calculate_evacuation_and_response(
        priority_category=event.priority,
        facility_type=fac_type,
        frp_max=event.max_frp,
        wind_speed_kmh=14.2,
        wind_direction_deg=215.0
    )
    plan["event_id"] = event.id
    plan["facility_id"] = event.nearest_facility_id
    plan["facility_name"] = event.facility.name if event.facility else "Unknown Regional Site"
    plan["event_centroid"] = {"latitude": event.centroid_lat, "longitude": event.centroid_lon}
    return plan

@router.get("/{event_id}/ics-201")
def get_event_ics_201_briefing(event_id: str, db: Session = Depends(get_db)):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    fac_type = event.facility.facility_type if event.facility else "none"
    fac_name = event.facility.name if event.facility else "Off-site / Unregistered Land Parcel"
    plan = RiskPriorityEngine.calculate_evacuation_and_response(
        priority_category=event.priority,
        facility_type=fac_type,
        frp_max=event.max_frp,
        wind_speed_kmh=14.2,
        wind_direction_deg=215.0
    )
    event_data = {
        "id": event.id,
        "source_class": event.source_class,
        "priority": event.priority,
        "priority_score": event.priority_score,
        "nearest_facility_name": fac_name,
        "centroid_lat": event.centroid_lat,
        "centroid_lon": event.centroid_lon,
        "max_frp": event.max_frp,
        "abnormality_state": getattr(event, "abnormality_state", "NORMAL"),
        "abnormality_score": getattr(event, "abnormality_score", 0.0)
    }
    return RiskPriorityEngine.generate_ics_201_brief(event_data, plan)


