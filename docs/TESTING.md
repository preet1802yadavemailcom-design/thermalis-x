# THERMALIS-X Comprehensive Testing Architecture

The THERMALIS-X test suite provides end-to-end verification across four distinct testing tiers:

1. **Unit Tests (`tests/unit/`)**:
   - `test_firms_ingestion.py`: Coordinate bounds validation, negative FRP filtering, SHA256 idempotency.
   - `test_baseline_engine.py`: Robust rolling median, MAD, and z-score excursion algorithms.
   - `test_event_engine.py`: ST-DBSCAN clustering, duration, area, and convex hull generation.
   - `test_risk_engine.py`: Multi-criteria priority scoring across accident and flaring scenarios.
   - `test_uncertainty_calibration.py`: Shannon entropy calculation, margin test, and Brier scoring.

2. **Integration Tests (`tests/integration/`)**:
   - `test_api_endpoints.py`: Tests all FastAPI endpoints (`/health`, `/events`, `/facilities`, `/alerts`, `/replay`).

3. **Scientific & Leakage Tests (`ml/evaluation/`)**:
   - `leakage_audit.py`: Confirms 0% facility overlap across train/test splits.
   - `train_baseline_ladder.py`: Verifies incremental F1 gains from Baseline 0 to Baseline 6.
   - `ablation_study.py`: Quantifies performance impact when removing baseline and morphology features.

4. **Formal Acceptance Tests (`scripts/run_acceptance_tests.py`)**:
   - Validates AT-001 through AT-015 with 100% pass rate.
