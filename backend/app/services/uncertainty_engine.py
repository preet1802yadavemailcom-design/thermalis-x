import math
from typing import Dict, Tuple
from backend.app.config import settings

class UncertaintyEngine:
    @staticmethod
    def compute_uncertainty(probabilities: Dict[str, float]) -> Tuple[float, float, bool]:
        # Shannon Entropy H(P) = - sum(p * log2(p))
        vals = [p for p in probabilities.values() if p > 1e-6]
        if not vals:
            return 1.0, 0.0, True

        total = sum(vals)
        norm_p = [p / total for p in vals]
        max_entropy = math.log2(len(norm_p)) if len(norm_p) > 1 else 1.0
        raw_entropy = -sum(p * math.log2(p) for p in norm_p)
        normalized_entropy = raw_entropy / max_entropy if max_entropy > 0 else 0.0

        # Margin between top 2 classes
        sorted_p = sorted(norm_p, reverse=True)
        margin = (sorted_p[0] - sorted_p[1]) if len(sorted_p) > 1 else 1.0

        # Abstention rule
        abstain = False
        if normalized_entropy > settings.UNCERTAINTY_THRESHOLD_ENTROPY or margin < settings.UNCERTAINTY_THRESHOLD_MARGIN:
            abstain = True

        return round(normalized_entropy, 3), round(margin, 3), abstain
