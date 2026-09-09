from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json
from typing import List

from backend.app.db.session import get_db
from backend.app.db.models import AnalystFeedback as FeedbackModel, Event as EventModel
from backend.app.schemas.feedback import AnalystFeedbackCreate, AnalystFeedbackOut, SupervisorApprovalRequest
from backend.app.services.evidence_ledger import EvidenceLedgerService

router = APIRouter()

@router.post("", response_model=AnalystFeedbackOut)
def submit_feedback(req: AnalystFeedbackCreate, db: Session = Depends(get_db)):
    event = db.query(EventModel).filter(EventModel.id == req.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {req.event_id} not found")

    # Anti-Poisoning & Quarantine Logic:
    # If the analyst proposes an override that directly contradicts high-confidence AI prediction,
    # quarantine the feedback for supervisor review before altering operational state.
    is_contradiction = (req.verified_class != event.source_class)
    high_ai_confidence = ((event.calibrated_prob or 0.0) >= 0.85)

    if is_contradiction and high_ai_confidence:
        feedback_status = "QUARANTINED"
        quarantine_reason = f"Override contradicts high-confidence model prediction ({event.source_class}, p={event.calibrated_prob:.2f}). Quarantined for supervisor review."
    else:
        feedback_status = "APPROVED"
        quarantine_reason = None

    fb = FeedbackModel(
        event_id=req.event_id,
        analyst_id=req.analyst_id or "lead_analyst_01",
        verified_class=req.verified_class,
        confidence=req.confidence,
        notes=f"{req.notes or ''} [Quarantine: {quarantine_reason}]" if quarantine_reason else req.notes,
        evidence_reviewed_json=json.dumps(req.evidence_reviewed),
        status=feedback_status
    )
    db.add(fb)

    # If immediately approved, apply state change and append to decision ledger
    if feedback_status == "APPROVED":
        prev_class = event.source_class
        event.source_class = req.verified_class
        
        EvidenceLedgerService.append_decision(
            db=db,
            event_id=event.id,
            decision_type="ANALYST_VERIFICATION",
            actor_id=fb.analyst_id,
            actor_role="ANALYST",
            previous_state=prev_class,
            new_state=req.verified_class,
            decision_payload={
                "action": "OVERRIDE_APPLIED",
                "analyst_id": fb.analyst_id,
                "confidence": req.confidence,
                "notes": req.notes,
                "evidence_reviewed": req.evidence_reviewed
            }
        )
    else:
        # Log quarantined submission to ledger
        EvidenceLedgerService.append_decision(
            db=db,
            event_id=event.id,
            decision_type="ANALYST_FEEDBACK_QUARANTINED",
            actor_id=fb.analyst_id,
            actor_role="ANALYST",
            previous_state=event.source_class,
            new_state=event.source_class,
            decision_payload={
                "action": "QUARANTINED_PENDING_SUPERVISOR",
                "proposed_class": req.verified_class,
                "reason": quarantine_reason
            }
        )

    db.commit()
    db.refresh(fb)

    return AnalystFeedbackOut(
        id=fb.id,
        event_id=fb.event_id,
        analyst_id=fb.analyst_id,
        verified_class=fb.verified_class,
        confidence=fb.confidence,
        notes=fb.notes,
        evidence_reviewed=req.evidence_reviewed,
        status=fb.status,
        supervisor_id=fb.supervisor_id,
        supervisor_notes=fb.supervisor_notes,
        created_at=fb.created_at
    )

@router.get("/quarantined", response_model=List[AnalystFeedbackOut])
def get_quarantined_feedback(db: Session = Depends(get_db)):
    """Lists all analyst feedback submissions currently in QUARANTINED state."""
    items = db.query(FeedbackModel).filter(FeedbackModel.status == "QUARANTINED").all()
    results = []
    for item in items:
        evidence = json.loads(item.evidence_reviewed_json) if item.evidence_reviewed_json else []
        results.append(AnalystFeedbackOut(
            id=item.id,
            event_id=item.event_id,
            analyst_id=item.analyst_id,
            verified_class=item.verified_class,
            confidence=item.confidence,
            notes=item.notes,
            evidence_reviewed=evidence,
            status=item.status,
            supervisor_id=item.supervisor_id,
            supervisor_notes=item.supervisor_notes,
            created_at=item.created_at
        ))
    return results

@router.post("/{feedback_id}/approve", response_model=AnalystFeedbackOut)
def approve_quarantined_feedback(
    feedback_id: str,
    req: SupervisorApprovalRequest,
    db: Session = Depends(get_db)
):
    """Supervisor endpoint to approve or reject quarantined analyst overrides."""
    fb = db.query(FeedbackModel).filter(FeedbackModel.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback entry not found")

    event = db.query(EventModel).filter(EventModel.id == fb.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Associated event not found")

    fb.supervisor_id = req.supervisor_id
    fb.supervisor_approved_at = datetime.now(timezone.utc)
    fb.supervisor_notes = req.supervisor_notes

    if req.approved:
        fb.status = "APPROVED"
        prev_class = event.source_class
        event.source_class = fb.verified_class

        EvidenceLedgerService.append_decision(
            db=db,
            event_id=event.id,
            decision_type="SUPERVISOR_APPROVAL",
            actor_id=req.supervisor_id,
            actor_role="SUPERVISOR",
            previous_state=prev_class,
            new_state=fb.verified_class,
            decision_payload={
                "action": "SUPERVISOR_APPROVED_OVERRIDE",
                "feedback_id": fb.id,
                "notes": req.supervisor_notes
            }
        )
    else:
        fb.status = "REJECTED"
        EvidenceLedgerService.append_decision(
            db=db,
            event_id=event.id,
            decision_type="SUPERVISOR_REJECTION",
            actor_id=req.supervisor_id,
            actor_role="SUPERVISOR",
            previous_state=event.source_class,
            new_state=event.source_class,
            decision_payload={
                "action": "SUPERVISOR_REJECTED_OVERRIDE",
                "feedback_id": fb.id,
                "notes": req.supervisor_notes
            }
        )

    db.commit()
    db.refresh(fb)

    evidence = json.loads(fb.evidence_reviewed_json) if fb.evidence_reviewed_json else []
    return AnalystFeedbackOut(
        id=fb.id,
        event_id=fb.event_id,
        analyst_id=fb.analyst_id,
        verified_class=fb.verified_class,
        confidence=fb.confidence,
        notes=fb.notes,
        evidence_reviewed=evidence,
        status=fb.status,
        supervisor_id=fb.supervisor_id,
        supervisor_notes=fb.supervisor_notes,
        created_at=fb.created_at
    )

@router.get("/events/{event_id}/ledger")
def get_event_ledger(event_id: str, db: Session = Depends(get_db)):
    """Fetches the cryptographic decision ledger and verification status for an event."""
    audit = EvidenceLedgerService.verify_event_ledger(db, event_id)
    return audit
