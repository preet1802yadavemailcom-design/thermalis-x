import pytest
from backend.app.services.firms_ingestion import FIRMSValidator

def test_firms_validation_valid():
    record = {
        "latitude": 17.7012,
        "longitude": 83.2568,
        "frp": 25.4,
        "brightness": 320.5,
        "acq_date": "2023-08-14",
        "acq_time": "1430",
        "satellite": "NOAA-20"
    }
    status, reasons = FIRMSValidator.validate_record(record)
    assert status == "VALID"
    assert len(reasons) == 0

def test_firms_validation_invalid_coords():
    record = {
        "latitude": 125.0,  # Out of bounds
        "longitude": 83.2568,
        "frp": 25.4,
        "acq_date": "2023-08-14"
    }
    status, reasons = FIRMSValidator.validate_record(record)
    assert status == "INVALID"
    assert "coordinates_out_of_bounds" in reasons

def test_firms_hash_idempotency():
    rec1 = {"satellite": "NOAA-20", "latitude": 17.7, "longitude": 83.2, "acq_date": "2023-08-14", "acq_time": "1430", "frp": 25.0}
    rec2 = {"satellite": "NOAA-20", "latitude": 17.7, "longitude": 83.2, "acq_date": "2023-08-14", "acq_time": "1430", "frp": 25.0}
    h1 = FIRMSValidator.compute_raw_hash(rec1)
    h2 = FIRMSValidator.compute_raw_hash(rec2)
    assert h1 == h2
