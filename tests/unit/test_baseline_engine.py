import pytest
from backend.app.services.baseline_engine import FacilityBaselineEngine

def test_facility_baseline_profiling():
    historical = [15.0, 18.0, 19.5, 22.0, 17.5, 18.2, 45.0]  # with one outlier
    profile = FacilityBaselineEngine.compute_baseline_profile(historical)
    assert profile["count"] == 7
    assert profile["median_frp"] == 18.2
    assert profile["mad_frp"] > 0

def test_baseline_excursion_detection():
    baseline = {
        "baseline_median_frp": 18.5,
        "baseline_mad_frp": 4.2,
        "baseline_p90_frp": 27.0,
        "baseline_p99_frp": 38.0
    }
    # Normal flaring: 22 MW
    norm_res = FacilityBaselineEngine.calculate_excursion(22.0, baseline)
    assert norm_res["is_baseline_excursion"] is False
    assert norm_res["frp_zscore"] < 2.0

    # Catastrophic fire: 280 MW
    fire_res = FacilityBaselineEngine.calculate_excursion(280.0, baseline)
    assert fire_res["is_baseline_excursion"] is True
    assert fire_res["frp_zscore"] > 10.0
