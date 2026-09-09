import numpy as np
from typing import Dict, List

class CalibrationService:
    @staticmethod
    def platt_scale(prob: float, a: float = 1.05, b: float = -0.02) -> float:
        # Standard Platt sigmoid calibration
        calibrated = 1.0 / (1.0 + np.exp(-(a * prob + b)))
        return float(np.clip(calibrated, 0.01, 0.99))

    @staticmethod
    def brier_score(y_true: List[int], y_prob: List[float]) -> float:
        # Lower Brier score means better calibration (0.0 is perfect)
        return float(np.mean((np.array(y_prob) - np.array(y_true)) ** 2))
