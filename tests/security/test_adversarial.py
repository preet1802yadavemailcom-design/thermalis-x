import pytest
import hashlib
from datetime import datetime, timezone
from backend.app.db.session import SessionLocal
from backend.app.db.models import Event, DecisionLedger, AnalystFeedback
from backend.app.services.evidence_ledger import EvidenceLedgerService
from backend.app.services.firms_ingestion import FIRMSValidator

def test_ledger_tamper_detection():
    db = SessionLocal()
    event_id = "EVT-TAMPER-TEST"
    try:
        # Clean previous test entries
        db.query(DecisionLedger).filter(DecisionLedger.event_id == event_id).delete()
        db.commit()

        # Append entry 1
        EvidenceLedgerService.append_decision(
            db=db,
            event_id=event_id,
            decision_type="AI_INFERENCE",
            actor_id="SYSTEM_XGB",
            actor_role="SYSTEM",
            previous_state=None,
            new_state="IND_ACCIDENT",
            decision_payload={"frp": 150.0}
        )
        # Append entry 2
        EvidenceLedgerService.append_decision(
            db=db,
            event_id=event_id,
            decision_type="ANALYST_VERIFICATION",
            actor_id="analyst_01",
            actor_role="ANALYST",
            previous_state="IND_ACCIDENT",
            new_state="IND_ACCIDENT",
            decision_payload={"notes": "All clear"}
        )
        db.commit()

        # Verify integrity initially passes
        initial_check = EvidenceLedgerService.verify_event_ledger(db, event_id)
        assert initial_check["is_valid"] is True
        assert initial_check["entries_verified"] == 2

        # Malicious attacker attempts direct database row tampering (e.g. changes payload without updating cryptographic hash)
        entry1 = db.query(DecisionLedger).filter(DecisionLedger.event_id == event_id, DecisionLedger.sequence_number == 1).first()
        entry1.decision_payload_json = '{"frp": 5000.0, "tampered": true}'
        db.commit()

        # Audit must immediately detect cryptographic tamper
        tamper_check = EvidenceLedgerService.verify_event_ledger(db, event_id)
        assert tamper_check["is_valid"] is False
        assert tamper_check["tampered_entry_id"] == entry1.id
        assert "mismatch" in tamper_check["reason"]
    finally:
        db.query(DecisionLedger).filter(DecisionLedger.event_id == event_id).delete()
        db.commit()
        db.close()

def test_firms_validator_adversarial_inputs():
    # Out of bounds latitude
    rec_bad_lat = {"satellite": "NOAA-20", "latitude": 95.0, "longitude": 80.0, "acq_date": "2023-08-14", "acq_time": "1200", "frp": 10.0}
    st, reason = FIRMSValidator.validate_record(rec_bad_lat)
    assert st == "INVALID"

    # Negative FRP
    rec_neg_frp = {"satellite": "NOAA-20", "latitude": 17.0, "longitude": 80.0, "acq_date": "2023-08-14", "acq_time": "1200", "frp": -5.0}
    st, reason = FIRMSValidator.validate_record(rec_neg_frp)
    assert st in ["SUSPECT", "INVALID"]
    assert "impossible_frp" in reason

    # Extreme unrealistic FRP (> 15,000 MW sensor glitch)
    rec_absurd_frp = {"satellite": "NOAA-20", "latitude": 17.0, "longitude": 80.0, "acq_date": "2023-08-14", "acq_time": "1200", "frp": 25000.0}
    st, reason = FIRMSValidator.validate_record(rec_absurd_frp)
    assert st in ["INVALID", "SUSPECT"]

    # Invalid timestamp
    rec_bad_time = {"satellite": "NOAA-20", "latitude": 17.0, "longitude": 80.0, "acq_date": "invalid-date", "acq_time": "9999", "frp": 20.0}
    st, reason = FIRMSValidator.validate_record(rec_bad_time)
    assert st == "INVALID"
