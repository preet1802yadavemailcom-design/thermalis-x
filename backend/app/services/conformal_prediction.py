import numpy as np
from typing import List, Dict, Tuple, Set

class SplitConformalPredictor:
    r"""
    Inductive Split Conformal Prediction for Multi-Class Classification.
    Provides finite-sample marginal coverage guarantees:
        P(Y \in C(X)) >= 1 - \alpha
    under the assumption of exchangeability of calibration and test points.
    """
    def __init__(self, alpha: float = 0.10):
        self.alpha = alpha
        self.q_hat = 1.0
        self.is_calibrated = False

    def calibrate(self, probs_calib: np.ndarray, y_calib: np.ndarray):
        r"""
        Compute nonconformity scores on hold-out calibration set:
            s_i = 1 - \hat{P}(Y = y_i | X_i)
        Compute empirical quantile threshold:
            \hat{q} = \lceil (n + 1)(1 - \alpha) \rceil / n
        """
        n = len(y_calib)
        if n == 0:
            return

        # True class predicted probabilities
        true_class_probs = probs_calib[np.arange(n), y_calib]
        nonconformity_scores = 1.0 - true_class_probs

        # Compute (1 - alpha) empirical quantile with finite-sample correction
        p_val = min(1.0, np.ceil((n + 1) * (1.0 - self.alpha)) / n)
        self.q_hat = float(np.quantile(nonconformity_scores, p_val, method="higher"))
        self.is_calibrated = True

    def predict_set(self, class_probs: Dict[str, float]) -> List[str]:
        r"""
        Construct conformal prediction set:
            C(X) = { c : 1 - \hat{P}(Y = c | X) <= \hat{q} }
                 = { c : \hat{P}(Y = c | X) >= 1 - \hat{q} }
        """
        threshold = max(0.01, 1.0 - self.q_hat) if self.is_calibrated else 0.15
        prediction_set = [c for c, p in class_probs.items() if p >= threshold]
        
        # Non-empty set guarantee
        if not prediction_set:
            top_class = max(class_probs, key=class_probs.get)
            prediction_set = [top_class]
            
        return prediction_set

    def evaluate_coverage(self, probs_test: np.ndarray, y_test: np.ndarray, class_names: List[str]) -> Tuple[float, float]:
        """
        Calculates empirical coverage and average set size on test partition.
        """
        n = len(y_test)
        covered = 0
        set_sizes = []
        for i in range(n):
            probs_dict = {class_names[c]: probs_test[i, c] for c in range(len(class_names))}
            c_set = self.predict_set(probs_dict)
            true_label = class_names[y_test[i]]
            if true_label in c_set:
                covered += 1
            set_sizes.append(len(c_set))
        return float(covered / n), float(np.mean(set_sizes))
