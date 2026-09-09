import pytest
from backend.app.services.risk_engine import RiskPriorityEngine

def test_risk_priority_scoring():
    # Refinery critical disaster
    cat, score = RiskPriorityEngine.calculate_priority(
        source_class="IND_ACCIDENT",
        calibrated_prob=0.92,
        frp_max=320.0,
        facility_type="refinery",
        uncertainty=0.1
    )
    assert cat == "CRITICAL"
    assert score >= 75.0

    # Normal flaring
    cat2, score2 = RiskPriorityEngine.calculate_priority(
        source_class="GAS_FLARE",
        calibrated_prob=0.90,
        frp_max=22.0,
        facility_type="refinery",
        uncertainty=0.1
    )
    assert cat2 == "INFORMATIONAL"
    assert score2 < 35.0
