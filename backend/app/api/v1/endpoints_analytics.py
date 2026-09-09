from fastapi import APIRouter, Depends
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
