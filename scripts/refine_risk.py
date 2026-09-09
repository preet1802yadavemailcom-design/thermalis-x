with open("backend/app/services/risk_engine.py", "r", encoding="utf-8") as f:
    code = f.read()

refined_code = """from typing import Dict, Any, Tuple

class RiskPriorityEngine:
    @staticmethod
    def calculate_priority(
        source_class: str,
        calibrated_prob: float,
        frp_max: float,
        facility_type: str = "none",
        uncertainty: float = 0.0
    ) -> Tuple[str, float]:
        # 1. Likelihood weight
        is_accident = (source_class == "IND_ACCIDENT")
        p_weight = calibrated_prob if is_accident else (0.05 * calibrated_prob)

        # 2. Thermal severity (0 to 1, scaled by 400 MW)
        s_therm = min(1.0, frp_max / 400.0)

        # 3. Facility criticality: full criticality applies to accidents; normal operations scale down
        criticality_map = {
            "refinery": 1.0,
            "petrochemical": 1.0,
            "chemical": 0.95,
            "power_plant": 0.85,
            "steel": 0.75,
            "ceramic_manufacturing": 0.60,
            "coal_mine": 0.50,
            "none": 0.10
        }
        base_criticality = criticality_map.get(facility_type, 0.2)
        c_fac = base_criticality if is_accident else (base_criticality * 0.20)

        # Weighted calculation (sum = 100)
        # 50% accident likelihood, 30% thermal magnitude, 20% facility criticality
        raw_score = (50.0 * p_weight) + (30.0 * s_therm) + (20.0 * c_fac)

        # Discount by uncertainty
        priority_score = raw_score * (1.0 - 0.4 * uncertainty)
        priority_score = round(max(5.0, min(99.0, priority_score)), 1)

        if priority_score >= 75.0:
            category = "CRITICAL"
        elif priority_score >= 55.0:
            category = "WARNING"
        elif priority_score >= 30.0:
            category = "WATCH"
        else:
            category = "INFORMATIONAL"

        return category, priority_score
"""

with open("backend/app/services/risk_engine.py", "w", encoding="utf-8") as f:
    f.write(refined_code)

print("Refined RiskPriorityEngine with operational hazard scaling.")
