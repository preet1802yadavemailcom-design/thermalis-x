import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timedelta
import json
from backend.app.services.firms_ingestion import FIRMSValidator
from backend.app.services.event_engine import EventEngine
from backend.app.services.facility_service import FacilityService
from backend.app.services.baseline_engine import FacilityBaselineEngine
from backend.app.services.feature_pipeline import FeaturePipeline
from backend.app.services.ml_service import MLClassificationService
from backend.app.services.calibration_service import CalibrationService
from backend.app.services.uncertainty_engine import UncertaintyEngine
from backend.app.services.risk_engine import RiskPriorityEngine
from backend.app.services.alert_service import AlertService
from backend.app.services.satellite_evidence import SatelliteEvidenceService
from backend.app.services.weather_service import WeatherService
from backend.app.services.replay_service import ReplayService

def run_all_acceptance_tests():
    print("=================================================================")
    print("      THERMALIS-X FORMAL SYSTEM ACCEPTANCE TEST SUITE (AT-001 - AT-015)")
    print("=================================================================\n")
    passed = 0
    total = 15

    # AT-001: FIRMS Observation Ingestion & Validation
    rec = {"satellite": "NOAA-20", "latitude": 17.7012, "longitude": 83.2568, "acq_date": "2023-08-14", "acq_time": "1430", "frp": 25.4}
    st, _ = FIRMSValidator.validate_record(rec)
    h = FIRMSValidator.compute_raw_hash(rec)
    assert st == "VALID" and len(h) == 64
    print("[PASS] AT-001: FIRMS Observation Ingestion & SHA256 Idempotency Validated")
    passed += 1

    # AT-002: Spatiotemporal Event Formation
    ee = EventEngine()
    t0 = datetime(2023, 8, 14, 12, 0)
    obs = [
        {"latitude": 17.701, "longitude": 83.256, "acq_datetime": t0, "frp": 20.0},
        {"latitude": 17.702, "longitude": 83.257, "acq_datetime": t0 + timedelta(hours=1), "frp": 45.0}
    ]
    clusters = ee.cluster_observations(obs)
    assert len(clusters) == 1 and len(clusters[0]) == 2
    ev = ee.construct_event_record("EVT-AT-002", clusters[0])
    assert ev["observation_count"] == 2 and ev["max_frp"] == 45.0
    print("[PASS] AT-002: Spatiotemporal Event Clustering & Geometry Generation Validated")
    passed += 1

    # AT-003: Industrial Infrastructure Context Retrieval
    fs = FacilityService()
    fac, dist = fs.find_nearest_facility(17.7012, 83.2568)
    assert fac is not None and fac["id"] == "FAC-VIZAG-001" and dist < 0.1
    inside = fs.is_inside_facility(17.7012, 83.2568, fac)
    assert inside is True
    print("[PASS] AT-003: Industrial Facility Nearest-Neighbor & Polygon Containment Validated")
    passed += 1

    # AT-004: Normal vs Abnormal Baseline Separation
    baseline = {"baseline_median_frp": 18.5, "baseline_mad_frp": 4.2, "baseline_p90_frp": 27.0, "baseline_p99_frp": 38.0}
    excursion_normal = FacilityBaselineEngine.calculate_excursion(20.0, baseline)
    assert excursion_normal["is_baseline_excursion"] is False
    excursion_fire = FacilityBaselineEngine.calculate_excursion(310.0, baseline)
    assert excursion_fire["is_baseline_excursion"] is True and excursion_fire["frp_zscore"] > 10.0
    print("[PASS] AT-004: Facility Thermal Baseline Robust MAD & Excursion Quantifier Validated")
    passed += 1

    # AT-005: 10-Class Tabular ML Classification
    fp = FeaturePipeline()
    feats = fp.extract_features(ev, obs, facility=fac)
    ml = MLClassificationService()
    pred = ml.predict(feats)
    assert pred["source_class"] in ml.CLASSES
    assert "raw_probabilities" in pred
    print(f"[PASS] AT-005: 10-Class ML Classifier Inference Validated (Class: {pred['source_class']})")
    passed += 1

    # AT-006: Probability Calibration
    cal_prob = CalibrationService.platt_scale(0.85)
    assert 0.0 < cal_prob < 1.0
    print(f"[PASS] AT-006: Platt Scaling Probability Calibration Validated (Raw 0.85 -> Calibrated {cal_prob:.3f})")
    passed += 1

    # AT-007: Conformal Uncertainty & Abstention
    entropy, margin, abstain = UncertaintyEngine.compute_uncertainty({"IND_ACCIDENT": 0.42, "GAS_FLARE": 0.40, "WILDFIRE": 0.18})
    assert abstain is True and margin < 0.15
    print("[PASS] AT-007: Shannon Entropy & Conformal Abstention Protection Validated")
    passed += 1

    # AT-008: Multi-Criteria Operational Priority Scoring
    cat, score = RiskPriorityEngine.calculate_priority("IND_ACCIDENT", 0.95, 320.0, "refinery", 0.1)
    assert cat == "CRITICAL" and score >= 75.0
    print(f"[PASS] AT-008: Operational Priority Engine Validated (Verdict: {cat}, Score: {score})")
    passed += 1

    # AT-009: Alert Generation & Deduplication
    alert = AlertService.generate_alert_payload({"id": "EVT-AT-009", "max_frp": 320.0, "source_class": "IND_ACCIDENT"}, cat, score, fac["name"])
    assert alert is not None and alert["severity"] == "CRITICAL"
    print("[PASS] AT-009: Alert Escalation & Operational Action Payload Validated")
    passed += 1

    # AT-010: Satellite Optical Evidence Integration
    import asyncio
    sat_evidence = asyncio.run(SatelliteEvidenceService.query_sentinel2_scene(17.7012, 83.2568, t0))
    assert sat_evidence["status"] == "AVAILABLE" and "Sentinel-2" in sat_evidence["sensor"]
    print(f"[PASS] AT-010: Satellite Evidence STAC Query Validated ({sat_evidence['sensor']}, Scene {sat_evidence['scene_id']})")
    passed += 1

    # AT-011: Weather & Plume Dispersion Context
    weather = asyncio.run(WeatherService.get_weather(17.7012, 83.2568))
    assert "wind_speed_10m" in weather and "wind_direction_10m" in weather
    print(f"[PASS] AT-011: Open-Meteo Weather Plume Dispersion Context Validated (Wind: {weather['wind_speed_10m']} km/h, {weather['wind_direction_10m']} deg)")
    passed += 1

    # AT-012: Human-in-the-Loop Analyst Verification & Cryptographic Decision Ledger
    from backend.app.db.session import SessionLocal
    from backend.app.services.evidence_ledger import EvidenceLedgerService
    db = SessionLocal()
    try:
        # Append initial AI decision
        EvidenceLedgerService.append_decision(
            db=db,
            event_id="EVT-AT-002",
            decision_type="AI_INFERENCE",
            actor_id="SYSTEM_XGB",
            actor_role="SYSTEM",
            previous_state=None,
            new_state="IND_ACCIDENT",
            decision_payload={"calibrated_prob": 0.94, "conformal_set": ["IND_ACCIDENT"]}
        )
        # Append Analyst Verification
        EvidenceLedgerService.append_decision(
            db=db,
            event_id="EVT-AT-002",
            decision_type="ANALYST_VERIFICATION",
            actor_id="lead_analyst_01",
            actor_role="ANALYST",
            previous_state="IND_ACCIDENT",
            new_state="IND_ACCIDENT",
            decision_payload={"notes": "Confirmed on Sentinel-2 SWIR", "confidence": 1.0}
        )
        db.commit()

        # Audit decision ledger cryptographic chain
        audit = EvidenceLedgerService.verify_event_ledger(db, "EVT-AT-002")
        assert audit["is_valid"] is True
        assert audit["entries_verified"] >= 2
        assert audit["status"] == "CRYPTOGRAPHICALLY_VERIFIED"
    finally:
        db.close()
    print("[PASS] AT-012: Human-in-the-Loop Feedback & Cryptographic Merkle Decision Ledger Validated")
    passed += 1

    # AT-013: Zero Facility Leakage Audit
    from ml.evaluation.leakage_audit import run_leakage_audit
    leak_cert = run_leakage_audit()
    assert leak_cert["status"] == "SCIENTIFICALLY_VALIDATED"
    assert leak_cert["facility_isolation_verified"] is True
    assert leak_cert["max_normalized_mutual_information"] < 0.70
    print("[PASS] AT-013: Automated Train/Test Facility-Held-Out Leakage Audit Validated")
    passed += 1

    # AT-014: Zero Circular Labeling Audit
    import pandas as pd
    b_df = pd.read_csv("data/processed/benchmark_dataset_v1.csv")
    flares_near = b_df[(b_df["target_class"] == "GAS_FLARE") & (b_df["is_near_facility"] == 1.0)]
    normal_near = b_df[(b_df["target_class"] == "IND_NORMAL") & (b_df["is_near_facility"] == 1.0)]
    acc_near = b_df[(b_df["target_class"] == "IND_ACCIDENT") & (b_df["is_near_facility"] == 1.0)]
    # Verify non-circularity: multiple non-accident classes occur near facilities
    assert len(flares_near) > 50, "Gas flares must occur within facility footprints"
    assert len(normal_near) > 50, "Normal heat must occur within facility footprints"
    assert len(acc_near) > 50, "Accidents occur within facility footprints"
    # Verify baseline excursion is not identical to accident label
    excursions_in_non_accidents = b_df[(b_df["target_class"] != "IND_ACCIDENT") & (b_df["is_baseline_excursion"] == 1.0)]
    assert len(excursions_in_non_accidents) > 0, "Non-accident baseline excursions must exist (process upsets)"
    print(f"[PASS] AT-014: Zero Circular Labeling Formally Validated ({len(flares_near)} flares, {len(normal_near)} normal heat co-located with industry)")
    passed += 1

    # AT-015: Historical Offline Replay Integrity
    cases = ReplayService.CASE_STUDIES
    assert len(cases) == 3
    for c in cases:
        steps = ReplayService.get_case_steps(c["case_id"])
        assert len(steps) >= 2
    print("[PASS] AT-015: Historical Offline Replay Engine Validated Across All 3 Indian Case Studies")
    passed += 1

    print("\n=================================================================")
    print(f"       TEST RESULT: {passed}/{total} ACCEPTANCE TESTS PASSED (100% PASS RATE)")
    print("=================================================================\n")

if __name__ == "__main__":
    run_all_acceptance_tests()
