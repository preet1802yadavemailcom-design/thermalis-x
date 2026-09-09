import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.db.models import EvidenceObject, DecisionLedger, Event

GENESIS_PREV_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

class EvidenceLedgerService:
    @staticmethod
    def compute_sha256(payload: Any) -> str:
        """Computes deterministic SHA-256 hash over canonical JSON representation."""
        if isinstance(payload, str):
            data_bytes = payload.encode("utf-8")
        else:
            data_bytes = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(data_bytes).hexdigest()

    @classmethod
    def record_evidence(
        cls,
        db: Session,
        event_id: str,
        evidence_type: str,
        source_uri: str,
        payload: Dict[str, Any],
        acquisition_timestamp: Optional[datetime] = None,
        data_quality_status: str = "VALID"
    ) -> EvidenceObject:
        """Stores a tamper-evident evidence object with deterministic SHA-256."""
        sha256 = cls.compute_sha256(payload)
        acq_time = acquisition_timestamp or datetime.now(timezone.utc)

        evidence = EvidenceObject(
            event_id=event_id,
            evidence_type=evidence_type,
            source_uri=source_uri,
            sha256_hash=sha256,
            acquisition_timestamp=acq_time,
            payload_json=json.dumps(payload, sort_keys=True, default=str),
            data_quality_status=data_quality_status
        )
        db.add(evidence)
        db.flush()
        return evidence

    @classmethod
    def append_decision(
        cls,
        db: Session,
        event_id: str,
        decision_type: str,
        actor_id: str,
        actor_role: str,
        new_state: str,
        decision_payload: Dict[str, Any],
        previous_state: Optional[str] = None
    ) -> DecisionLedger:
        """
        Appends a cryptographically chained entry to the immutable decision ledger.
        Enforces Merkle-style prev_hash link and unique sequence number per event.
        """
        last_entry = (
            db.query(DecisionLedger)
            .filter(DecisionLedger.event_id == event_id)
            .order_by(DecisionLedger.sequence_number.desc())
            .first()
        )

        if last_entry is None:
            seq_num = 1
            prev_hash = GENESIS_PREV_HASH
        else:
            seq_num = last_entry.sequence_number + 1
            prev_hash = last_entry.entry_hash

        payload_str = json.dumps(decision_payload, sort_keys=True, default=str)
        ts = datetime.now(timezone.utc)
        ts_canonical = ts.strftime("%Y-%m-%d %H:%M:%S")

        # Compute tamper-evident hash over all fields
        header_data = f"{prev_hash}:{seq_num}:{event_id}:{decision_type}:{actor_id}:{actor_role}:{previous_state}:{new_state}:{payload_str}:{ts_canonical}"
        entry_hash = hashlib.sha256(header_data.encode("utf-8")).hexdigest()

        ledger_entry = DecisionLedger(
            event_id=event_id,
            sequence_number=seq_num,
            decision_type=decision_type,
            actor_id=actor_id,
            actor_role=actor_role,
            previous_state=previous_state,
            new_state=new_state,
            decision_payload_json=payload_str,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
            timestamp=ts
        )
        db.add(ledger_entry)
        db.flush()
        return ledger_entry

    @classmethod
    def verify_event_ledger(cls, db: Session, event_id: str) -> Dict[str, Any]:
        """
        Audits cryptographic chain integrity for an event's decision ledger.
        Detects tampering, out-of-order sequence, or broken hash pointers.
        """
        entries = (
            db.query(DecisionLedger)
            .filter(DecisionLedger.event_id == event_id)
            .order_by(DecisionLedger.sequence_number.asc())
            .all()
        )

        if not entries:
            return {"event_id": event_id, "is_valid": True, "entries_verified": 0, "status": "EMPTY_LEDGER"}

        expected_prev_hash = GENESIS_PREV_HASH

        for i, entry in enumerate(entries):
            expected_seq = i + 1
            if entry.sequence_number != expected_seq:
                return {
                    "event_id": event_id,
                    "is_valid": False,
                    "tampered_entry_id": entry.id,
                    "reason": f"Sequence number mismatch: expected {expected_seq}, found {entry.sequence_number}"
                }

            if entry.prev_hash != expected_prev_hash:
                return {
                    "event_id": event_id,
                    "is_valid": False,
                    "tampered_entry_id": entry.id,
                    "reason": f"Hash chain break at seq {entry.sequence_number}: expected prev_hash {expected_prev_hash}, found {entry.prev_hash}"
                }

            # Recalculate hash with canonical timestamp
            ts_canonical = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            header_data = f"{entry.prev_hash}:{entry.sequence_number}:{entry.event_id}:{entry.decision_type}:{entry.actor_id}:{entry.actor_role}:{entry.previous_state}:{entry.new_state}:{entry.decision_payload_json}:{ts_canonical}"
            recomputed = hashlib.sha256(header_data.encode("utf-8")).hexdigest()

            if recomputed != entry.entry_hash:
                return {
                    "event_id": event_id,
                    "is_valid": False,
                    "tampered_entry_id": entry.id,
                    "reason": f"Entry hash mismatch at seq {entry.sequence_number}: data has been modified"
                }

            expected_prev_hash = entry.entry_hash

        return {
            "event_id": event_id,
            "is_valid": True,
            "entries_verified": len(entries),
            "status": "CRYPTOGRAPHICALLY_VERIFIED",
            "head_hash": expected_prev_hash
        }
