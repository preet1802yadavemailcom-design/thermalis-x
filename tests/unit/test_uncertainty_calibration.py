import pytest
from backend.app.services.uncertainty_engine import UncertaintyEngine
from backend.app.services.calibration_service import CalibrationService

def test_uncertainty_and_abstention():
    # High confidence case
    confident_probs = {"IND_ACCIDENT": 0.92, "GAS_FLARE": 0.05, "WILDFIRE": 0.03}
    entropy, margin, abstain = UncertaintyEngine.compute_uncertainty(confident_probs)
    assert abstain is False
    assert margin > 0.8

    # Ambiguous case -> Abstain
    ambiguous_probs = {"IND_ACCIDENT": 0.41, "GAS_FLARE": 0.39, "WILDFIRE": 0.20}
    entropy2, margin2, abstain2 = UncertaintyEngine.compute_uncertainty(ambiguous_probs)
    assert abstain2 is True
    assert margin2 < 0.15

def test_calibration_brier_score():
    y_true = [1, 0, 1, 1]
    y_prob = [0.9, 0.1, 0.85, 0.95]
    brier = CalibrationService.brier_score(y_true, y_prob)
    assert brier < 0.05
