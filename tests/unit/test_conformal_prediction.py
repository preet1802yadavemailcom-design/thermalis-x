import numpy as np
import pytest
from backend.app.services.conformal_prediction import SplitConformalPredictor

def test_conformal_initialization():
    cp = SplitConformalPredictor(alpha=0.10)
    assert cp.alpha == 0.10
    assert not cp.is_calibrated
    assert cp.q_hat == 1.0

def test_conformal_calibration_and_coverage():
    np.random.seed(42)
    cp = SplitConformalPredictor(alpha=0.10)
    
    n_calib = 500
    n_classes = 5
    # Simulate well-separated probabilities
    logits_calib = np.random.randn(n_calib, n_classes)
    y_calib = np.random.randint(0, n_classes, size=n_calib)
    # Boost true class logit
    logits_calib[np.arange(n_calib), y_calib] += 2.5
    exp_l = np.exp(logits_calib - np.max(logits_calib, axis=1, keepdims=True))
    probs_calib = exp_l / np.sum(exp_l, axis=1, keepdims=True)
    
    cp.calibrate(probs_calib, y_calib)
    assert cp.is_calibrated
    assert 0.0 < cp.q_hat < 1.0

    # Test coverage on test partition
    n_test = 400
    logits_test = np.random.randn(n_test, n_classes)
    y_test = np.random.randint(0, n_classes, size=n_test)
    logits_test[np.arange(n_test), y_test] += 2.5
    exp_lt = np.exp(logits_test - np.max(logits_test, axis=1, keepdims=True))
    probs_test = exp_lt / np.sum(exp_lt, axis=1, keepdims=True)
    
    class_names = [f'CLASS_{i}' for i in range(n_classes)]
    coverage, avg_size = cp.evaluate_coverage(probs_test, y_test, class_names)
    
    # Statistical guarantee check: coverage should be >= 1 - alpha - small tolerance
    assert coverage >= (1.0 - cp.alpha - 0.05)
    assert avg_size >= 1.0

def test_conformal_non_empty_guarantee():
    cp = SplitConformalPredictor(alpha=0.10)
    cp.q_hat = 0.01  # Very strict threshold
    cp.is_calibrated = True
    
    probs = {'A': 0.005, 'B': 0.004, 'C': 0.001}
    c_set = cp.predict_set(probs)
    assert len(c_set) >= 1
    assert 'A' in c_set

def test_conformal_multi_class_inclusion():
    cp = SplitConformalPredictor(alpha=0.10)
    cp.q_hat = 0.70  # threshold: p >= 0.30
    cp.is_calibrated = True
    
    probs = {'IND_ACCIDENT': 0.45, 'GAS_FLARE': 0.40, 'WILDFIRE': 0.10, 'AGRI_BURN': 0.05}
    c_set = cp.predict_set(probs)
    assert 'IND_ACCIDENT' in c_set
    assert 'GAS_FLARE' in c_set
    assert 'AGRI_BURN' not in c_set
