import numpy as np
from typing import List, Dict, Any

class FacilityBaselineEngine:
    @staticmethod
    def compute_baseline_profile(historical_frp: List[float]) -> Dict[str, float]:
        if not historical_frp:
            return {
                "median_frp": 0.0,
                "mad_frp": 0.0,
                "p10_frp": 0.0,
                "p90_frp": 0.0,
                "p99_frp": 0.0,
                "count": 0
            }
        arr = np.array(historical_frp, dtype=float)
        median = float(np.median(arr))
        # Median Absolute Deviation (MAD)
        mad = float(np.median(np.abs(arr - median)))
        p10 = float(np.percentile(arr, 10))
        p90 = float(np.percentile(arr, 90))
        p99 = float(np.percentile(arr, 99))
        return {
            "median_frp": round(median, 2),
            "mad_frp": round(mad, 2),
            "p10_frp": round(p10, 2),
            "p90_frp": round(p90, 2),
            "p99_frp": round(p99, 2),
            "count": len(arr)
        }

    @staticmethod
    def calculate_excursion(current_frp: float, baseline: Dict[str, Any]) -> Dict[str, Any]:
        median = baseline.get("baseline_median_frp", 0.0)
        mad = baseline.get("baseline_mad_frp", 0.0)
        p90 = baseline.get("baseline_p90_frp", 0.0)
        p99 = baseline.get("baseline_p99_frp", 0.0)

        # Scale factor 1.4826 makes MAD an unbiased estimator of standard deviation for normal dist
        sigma_robust = 1.4826 * mad if mad > 0.01 else 2.0
        z_score = (current_frp - median) / sigma_robust

        is_excursion = (current_frp > p99) or (z_score > 3.0)
        ratio = current_frp / max(1.0, median)

        return {
            "frp_zscore": round(float(z_score), 2),
            "frp_to_baseline_ratio": round(float(ratio), 2),
            "is_baseline_excursion": bool(is_excursion),
            "exceeds_p90": bool(current_frp > p90),
            "exceeds_p99": bool(current_frp > p99)
        }
