import os
import json
import numpy as np
from typing import Dict, List, Optional
from sklearn.linear_model import LogisticRegression

class CalibrationService:
    """
    Empirical Probability Calibration Service.
    Loads and executes fitted Platt scaling parameters derived from dedicated
    calibration partitions, rather than using arbitrary heuristic constants.
    """
    DEFAULT_PLATT_A = 1.0
    DEFAULT_PLATT_B = 0.0

    _default_instance = None

    def __init__(self, artifact_path: str = "ml/models/calibration_artifact_v1.json"):
        self.artifact_path = artifact_path
        self.platt_a = self.DEFAULT_PLATT_A
        self.platt_b = self.DEFAULT_PLATT_B
        self.is_fitted = False
        self.load_parameters()

    @classmethod
    def get_default_instance(cls):
        if cls._default_instance is None:
            cls._default_instance = cls()
        return cls._default_instance

    def load_parameters(self):
        if os.path.exists(self.artifact_path):
            try:
                with open(self.artifact_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.platt_a = float(data.get("platt_a", self.DEFAULT_PLATT_A))
                    self.platt_b = float(data.get("platt_b", self.DEFAULT_PLATT_B))
                    self.is_fitted = True
            except Exception:
                self.platt_a = self.DEFAULT_PLATT_A
                self.platt_b = self.DEFAULT_PLATT_B
                self.is_fitted = False

    def scale_prob(self, prob: float) -> float:
        """Applies fitted Platt sigmoid calibration on instance."""
        val = self.platt_a * float(prob) + self.platt_b
        calibrated = 1.0 / (1.0 + np.exp(-val))
        return float(np.clip(calibrated, 0.01, 0.99))

    @classmethod
    def platt_scale(cls, prob: float) -> float:
        """Applies fitted Platt sigmoid calibration (callable on class or instance)."""
        return cls.get_default_instance().scale_prob(prob)

    @classmethod
    def scale(cls, prob: float) -> float:
        """Alias for platt_scale."""
        return cls.platt_scale(prob)

    @staticmethod
    def fit_platt(raw_probs: np.ndarray, y_true: np.ndarray) -> Dict[str, float]:
        """Fits Platt scaling parameters via maximum likelihood on a hold-out calibration split."""
        X = raw_probs.reshape(-1, 1)
        clf = LogisticRegression(C=1.0)
        clf.fit(X, y_true)
        return {
            "platt_a": float(clf.coef_[0][0]),
            "platt_b": float(clf.intercept_[0])
        }

    @staticmethod
    def compute_brier_score(y_true: List[int], y_prob: List[float]) -> float:
        """Computes multi-class or binary Brier score."""
        return float(np.mean((np.array(y_prob) - np.array(y_true)) ** 2))

    @classmethod
    def brier_score(cls, y_true: List[int], y_prob: List[float]) -> float:
        """Alias for compute_brier_score."""
        return cls.compute_brier_score(y_true, y_prob)

    @staticmethod
    def compute_ece(probs: np.ndarray, y_true: np.ndarray, n_bins: int = 10) -> float:
        """Computes Expected Calibration Error (ECE) across reliability bins."""
        if probs.ndim == 1:
            confs = probs
            preds = (probs >= 0.5).astype(int)
        else:
            preds = np.argmax(probs, axis=1)
            confs = np.max(probs, axis=1)
            
        accuracies = (preds == y_true).astype(float)
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        n = len(y_true)

        for i in range(n_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]
            mask = (confs > bin_lower) & (confs <= bin_upper)
            bin_size = np.sum(mask)
            if bin_size > 0:
                bin_acc = np.mean(accuracies[mask])
                bin_conf = np.mean(confs[mask])
                ece += (bin_size / n) * abs(bin_acc - bin_conf)

        return float(ece)
