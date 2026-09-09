from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.db.session import get_db
from backend.app.db.models import Facility as FacilityModel
from backend.app.schemas.facility import FacilityOut

router = APIRouter()

@router.get("", response_model=List[FacilityOut])
def list_facilities(db: Session = Depends(get_db)):
    facs = db.query(FacilityModel).all()
    return [FacilityOut.model_validate(f) for f in facs]

@router.get("/{facility_id}", response_model=FacilityOut)
def get_facility(facility_id: str, db: Session = Depends(get_db)):
    fac = db.query(FacilityModel).filter(FacilityModel.id == facility_id).first()
    if not fac:
        raise HTTPException(status_code=404, detail=f"Facility {facility_id} not found")
    return FacilityOut.model_validate(fac)
