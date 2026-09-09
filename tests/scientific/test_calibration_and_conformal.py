import pytest
import numpy as np
from backend.app.services.calibration_service import CalibrationService
from backend.app.services.conformal_prediction import SplitConformalPredictor
from backend.app.services.uncertainty_engine import UncertaintyEngine

def test_calibration_ece_and_brier():
    y_true = np.array([1, 1, 0, 0, 1, 0, 1, 1, 0, 0])
    probs = np.array([
        [0.1, 0.9],
        [0.2, 0.8],
        [0.85, 0.15],
        [0.9, 0.1],
        [0.15, 0.85],
        [0.7, 0.3],
        [0.05, 0.95],
        [0.25, 0.75],
        [0.95, 0.05],
        [0.8, 0.2]
    ])

    ece = CalibrationService.compute_ece(probs, y_true)
    assert 0.0 <= ece <= 0.20

    y_true_binary = [1, 0, 1, 1]
    y_prob_binary = [0.95, 0.05, 0.90, 0.85]
    brier = CalibrationService.brier_score(y_true_binary, y_prob_binary)
    assert brier < 0.05

def test_split_conformal_decision_policy():
    cp = SplitConformalPredictor(alpha=0.10)
    cp.q_hat = 0.50
    cp.is_calibrated = True

    # Singleton set with low entropy -> ACCEPT
    single_res = cp.determine_decision_policy(
        prediction_set=["IND_ACCIDENT"],
        entropy=0.25,
        top_prob=0.92
    )
    assert single_res["policy_action"] == "ACCEPT"
    assert single_res["abstain_recommended"] is False

    # Ambiguous set with 2 classes -> REVIEW
    ambig_res = cp.determine_decision_policy(
        prediction_set=["IND_ACCIDENT", "GAS_FLARE"],
        entropy=0.55,
        top_prob=0.52
    )
    assert ambig_res["policy_action"] == "REVIEW"

    # Degraded set with 3+ classes or UNCERTAIN -> ABSTAIN
    abstain_res = cp.determine_decision_policy(
        prediction_set=["IND_ACCIDENT", "GAS_FLARE", "WILDFIRE"],
        entropy=0.85,
        top_prob=0.38
    )
    assert abstain_res["policy_action"] == "ABSTAIN"
    assert abstain_res["abstain_recommended"] is True

def test_shannon_entropy_information_theoretic_invariance():
    # Uniform distribution across 4 classes has maximum entropy ln(4) ~ 1.386 nats
    uniform_probs = {"A": 0.25, "B": 0.25, "C": 0.25, "D": 0.25}
    entropy_max, margin, abstain = UncertaintyEngine.compute_uncertainty(uniform_probs)
    assert abstain is True
    assert margin == 0.0
    assert entropy_max > 0.60

    # Deterministic degenerate distribution has zero entropy
    degenerate_probs = {"A": 1.0, "B": 0.0, "C": 0.0, "D": 0.0}
    entropy_zero, margin_deg, abstain_deg = UncertaintyEngine.compute_uncertainty(degenerate_probs)
    assert abstain_deg is False
    assert margin_deg == 1.0
    assert entropy_zero == 0.0
