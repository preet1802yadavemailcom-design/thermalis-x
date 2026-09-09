import os
import json
import numpy as np
from typing import List, Dict, Tuple, Set, Any, Optional

class ConformalCoverageResult(dict):
    """Container that behaves both as a dict and a 2-tuple (marginal_coverage, average_set_size) for unpacking."""
    def __iter__(self):
        yield self["marginal_coverage"]
        yield self["average_set_size"]

class SplitConformalPredictor:
    r"""
    Inductive Split Conformal Prediction for Multi-Class Classification.
    Provides finite-sample marginal coverage guarantees:
        P(Y \in C(X)) >= 1 - \alpha
    under the assumption of exchangeability of calibration and test points.
    """
    def __init__(self, alpha: float = 0.10, artifact_path: Optional[str] = None):
        self.alpha = alpha
        self.artifact_path = artifact_path
        self.q_hat = 1.0
        self.is_calibrated = False
        if artifact_path:
            self.load_parameters()

    @classmethod
    def load_from_artifact(cls, artifact_path: str = "ml/models/conformal_artifact_v1.json", alpha: float = 0.10) -> "SplitConformalPredictor":
        predictor = cls(alpha=alpha, artifact_path=artifact_path)
        return predictor

    def load_parameters(self):
        if self.artifact_path and os.path.exists(self.artifact_path):
            try:
                with open(self.artifact_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.q_hat = float(data.get("q_hat", 1.0))
                    self.alpha = float(data.get("alpha", self.alpha))
                    self.is_calibrated = True
            except Exception:
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

        true_class_probs = probs_calib[np.arange(n), y_calib]
        nonconformity_scores = 1.0 - true_class_probs

        p_val = min(1.0, np.ceil((n + 1) * (1.0 - self.alpha)) / n)
        self.q_hat = float(np.quantile(nonconformity_scores, p_val, method="higher"))
        self.is_calibrated = True

    def predict_set(self, class_probs: Dict[str, float]) -> List[str]:
        r"""
        Construct conformal prediction set:
            C(X) = { c : 1 - \hat{P}(Y = c | X) <= \hat{q} }
                 = { c : \hat{P}(Y = c | X) >= 1 - \hat{q} }
        """
        threshold = max(0.01, 1.0 - self.q_hat)
        prediction_set = [c for c, p in class_probs.items() if p >= threshold]
        
        # Non-empty set guarantee
        if not prediction_set:
            top_class = max(class_probs, key=class_probs.get)
            prediction_set = [top_class]
            
        return sorted(prediction_set, key=lambda c: class_probs.get(c, 0.0), reverse=True)

    def determine_decision_policy(
        self,
        prediction_set: List[str],
        entropy: float,
        top_prob: float
    ) -> Dict[str, Any]:
        """
        Selective Risk Accept/Review/Abstain Decision Policy.
        - ACCEPT: High-confidence single-class prediction set (|C(X)| == 1) with low entropy.
        - REVIEW: Ambiguous prediction set (|C(X)| > 1) requiring analyst triage.
        - ABSTAIN: High uncertainty / degraded evidence, prompting optical satellite tasking.
        """
        set_size = len(prediction_set)
        
        if set_size == 1 and entropy < 0.50 and top_prob >= 0.70:
            action = "ACCEPT"
            rationale = "High statistical certainty: conformal set is singleton and entropy is below threshold."
        elif "UNCERTAIN" in prediction_set or entropy >= 0.60 or set_size >= 3:
            action = "ABSTAIN"
            rationale = "High uncertainty or degraded evidence: queueing optical Sentinel-2 high-resolution tasking."
        else:
            action = "REVIEW"
            rationale = f"Multi-class ambiguity: conformal prediction set contains {set_size} plausible candidate hypotheses."

        return {
            "policy_action": action,
            "rationale": rationale,
            "conformal_set_size": set_size,
            "prediction_set": prediction_set,
            "abstain_recommended": (action == "ABSTAIN")
        }

    def evaluate_coverage(
        self,
        probs_test: np.ndarray,
        y_test: np.ndarray,
        class_names: List[str]
    ) -> Dict[str, Any]:
        """
        Calculates empirical marginal coverage, class-conditional coverage, and set efficiency.
        """
        n = len(y_test)
        covered = 0
        set_sizes = []
        class_covered = {c: 0 for c in class_names}
        class_totals = {c: 0 for c in class_names}

        for i in range(n):
            probs_dict = {class_names[c]: probs_test[i, c] for c in range(len(class_names))}
            c_set = self.predict_set(probs_dict)
            true_label = class_names[y_test[i]]
            
            class_totals[true_label] += 1
            if true_label in c_set:
                covered += 1
                class_covered[true_label] += 1
            set_sizes.append(len(c_set))

        class_coverage = {}
        for c in class_names:
            tot = class_totals[c]
            class_coverage[c] = round(class_covered[c] / tot, 4) if tot > 0 else 1.0

        return ConformalCoverageResult({
            "marginal_coverage": round(float(covered / n), 4),
            "average_set_size": round(float(np.mean(set_sizes)), 2),
            "single_class_ratio": round(float(np.mean([1 for s in set_sizes if s == 1]) / n), 4),
            "class_conditional_coverage": class_coverage
        })
