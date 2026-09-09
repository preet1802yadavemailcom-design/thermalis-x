from fastapi import APIRouter, HTTPException
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
