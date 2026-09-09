from fastapi import APIRouter, Depends, HTTPException
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
    return [AlertOut.model_validate(a) for a in alerts]

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
    return AlertOut.model_validate(alert)
