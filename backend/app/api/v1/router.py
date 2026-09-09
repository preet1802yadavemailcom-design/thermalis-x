from fastapi import APIRouter
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
