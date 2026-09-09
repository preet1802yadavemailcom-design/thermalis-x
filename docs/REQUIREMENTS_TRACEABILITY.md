# THERMALIS-X Requirements Traceability Matrix (RTM)

| Requirement Code | Description | Implementation File | Verification Test | Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | Multi-sensor FIRMS Ingestion (NOAA-20/21, MODIS) | `backend/app/services/firms_ingestion.py` | `tests/unit/test_firms_ingestion.py` (AT-001) | VERIFIED |
| **REQ-02** | Spatiotemporal Event Clustering (Adaptive ST-DBSCAN) | `backend/app/services/event_engine.py` | `tests/unit/test_event_engine.py` (AT-002) | VERIFIED |
| **REQ-03** | Industrial Infrastructure Context Retrieval | `backend/app/services/facility_service.py` | `tests/unit/test_event_engine.py` (AT-003) | VERIFIED |
| **REQ-04** | Facility Historical Baseline & Excursion Detection | `backend/app/services/baseline_engine.py` | `tests/unit/test_baseline_engine.py` (AT-004) | VERIFIED |
| **REQ-05** | 10-Class Tabular ML Classification | `backend/app/services/ml_service.py` | `ml/training/train_xgboost.py` (AT-005) | VERIFIED |
| **REQ-06** | Probability Calibration (Platt Sigmoid Scaling) | `backend/app/services/calibration_service.py` | `tests/unit/test_uncertainty_calibration.py` (AT-006) | VERIFIED |
| **REQ-07** | Conformal Uncertainty & Abstention Protection | `backend/app/services/uncertainty_engine.py` | `tests/unit/test_uncertainty_calibration.py` (AT-007) | VERIFIED |
| **REQ-08** | Multi-Criteria Operational Priority Scoring | `backend/app/services/risk_engine.py` | `tests/unit/test_risk_engine.py` (AT-008) | VERIFIED |
| **REQ-09** | Alert Generation & Deduplication Engine | `backend/app/services/alert_service.py` | `tests/integration/test_api_endpoints.py` (AT-009) | VERIFIED |
| **REQ-10** | Multimodal Satellite Optical Evidence (Sentinel-2) | `backend/app/services/satellite_evidence.py` | `scripts/run_acceptance_tests.py` (AT-010) | VERIFIED |
| **REQ-11** | Open-Meteo Weather Plume Vector Integration | `backend/app/services/weather_service.py` | `scripts/run_acceptance_tests.py` (AT-011) | VERIFIED |
| **REQ-12** | Human-in-the-Loop Ground Truth Feedback & Audit | `backend/app/api/v1/endpoints_feedback.py` | `tests/integration/test_api_endpoints.py` (AT-012) | VERIFIED |
| **REQ-13** | Zero Facility Leakage Audit | `ml/evaluation/leakage_audit.py` | `ml/evaluation/leakage_audit.py` (AT-013) | VERIFIED |
| **REQ-14** | Zero Circular Labeling Audit | `ml/evaluation/leakage_audit.py` | `ml/evaluation/leakage_audit.py` (AT-014) | VERIFIED |
| **REQ-15** | Historical Offline Replay Mode across 3 Cases | `backend/app/services/replay_service.py` | `tests/integration/test_api_endpoints.py` (AT-015) | VERIFIED |
