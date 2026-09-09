from fastapi import APIRouter, Depends
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
    return AnalystFeedbackOut.model_validate(fb)
