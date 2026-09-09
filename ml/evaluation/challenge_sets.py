import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List
import xgboost as xgb

from ml.training.dataset_builder import DatasetBuilder
from backend.app.services.ml_service import MLClassificationService
from backend.app.services.conformal_prediction import SplitConformalPredictor

class ChallengeSetBenchmark:
    """
    Evaluates THERMALIS-X under rigorous operational stress conditions.
    Challenge Sets:
      1. Cloud Obscuration (1-2 obs, sparse detection, intermittent visibility)
      2. Missing Weather Data (defaults, no meteorological reanalysis)
      3. Unmapped / Missing Facility Boundary (unregistered infrastructure)
      4. Novel Facility Types (zero-shot industrial categories)
      5. Catastrophic Extreme FRP (> 1200 MW runaway thermal release)
      6. Wildfire Adjacency (wildfire within 1 km of chemical refinery perimeter)
    """

    @classmethod
    def generate_challenge_datasets(cls, n_per_challenge: int = 150) -> Dict[str, pd.DataFrame]:
        np.random.seed(1337)
        datasets = {}

        # 1. Cloud Obscuration (Flares/fires masked by monsoon cloud decks)
        cloud_rows = []
        for i in range(n_per_challenge):
            target = np.random.choice(["IND_ACCIDENT", "GAS_FLARE", "WILDFIRE", "IND_NORMAL"])
            is_ind = target in ["IND_ACCIDENT", "GAS_FLARE", "IND_NORMAL"]
            cloud_rows.append({
                "challenge_id": f"CLOUD_{i:04d}",
                "challenge_type": "Cloud_Obscuration",
                "target_class": target,
                "frp_mean": float(np.random.uniform(20.0, 90.0)),
                "frp_max": float(np.random.uniform(30.0, 110.0)),
                "frp_trend": float(np.random.uniform(-5.0, 5.0)),
                "dist_to_facility_km": float(np.random.uniform(0.1, 0.9) if is_ind else np.random.uniform(5.0, 30.0)),
                "is_near_facility": 1.0 if is_ind else 0.0,
                "area_ha": float(np.random.uniform(0.5, 2.0)),
                "duration_hours": float(np.random.uniform(0.1, 1.0)), # Truncated by cloud gap
                "frp_zscore": float(np.random.uniform(1.0, 4.5) if target == "IND_ACCIDENT" else np.random.uniform(0.1, 1.8)),
                "is_baseline_excursion": 1.0 if target == "IND_ACCIDENT" else 0.0,
                "landcover_class": 3.0 if is_ind else (1.0 if target == "WILDFIRE" else 2.0),
                "is_refinery": 1.0 if is_ind else 0.0,
                "is_coal_mine": 0.0,
                "is_power_plant": 0.0,
                "compactness": float(np.random.uniform(0.6, 0.95)),
                "persistence_ratio": float(np.random.uniform(0.05, 0.25)), # Depressed by missing observations
                "spread_velocity": float(np.random.uniform(0.0, 0.1))
            })
        datasets["Cloud_Obscuration"] = pd.DataFrame(cloud_rows)

        # 2. Missing Weather (Meteorological API failure fallback)
        weather_rows = []
        for i in range(n_per_challenge):
            target = np.random.choice(DatasetBuilder.CLASSES)
            is_ind = target in ["IND_ACCIDENT", "IND_NORMAL", "GAS_FLARE", "POWER_HEAT", "MINE_HEAT"]
            weather_rows.append({
                "challenge_id": f"NO_WX_{i:04d}",
                "challenge_type": "Missing_Weather",
                "target_class": target,
                "frp_mean": float(np.random.uniform(15.0, 140.0)),
                "frp_max": float(np.random.uniform(25.0, 220.0)),
                "frp_trend": float(np.random.uniform(-10.0, 20.0)),
                "dist_to_facility_km": float(np.random.uniform(0.1, 1.2) if is_ind else np.random.uniform(4.0, 40.0)),
                "is_near_facility": 1.0 if is_ind else 0.0,
                "area_ha": float(np.random.uniform(0.5, 12.0)),
                "duration_hours": float(np.random.uniform(1.0, 48.0)),
                "frp_zscore": float(np.random.uniform(4.0, 9.0) if target == "IND_ACCIDENT" else np.random.uniform(0.0, 1.5)),
                "is_baseline_excursion": 1.0 if target == "IND_ACCIDENT" else 0.0,
                "landcover_class": 3.0 if is_ind else 1.0,
                "is_refinery": 1.0 if target in ["GAS_FLARE", "IND_ACCIDENT"] else 0.0,
                "is_coal_mine": 1.0 if target == "MINE_HEAT" else 0.0,
                "is_power_plant": 1.0 if target == "POWER_HEAT" else 0.0,
                "compactness": float(np.random.uniform(0.4, 0.9)),
                "persistence_ratio": float(np.random.uniform(0.3, 0.9)),
                "spread_velocity": float(np.random.uniform(0.0, 0.4))
            })
        datasets["Missing_Weather"] = pd.DataFrame(weather_rows)

        # 3. Unmapped / Missing Facility Boundary (Greenfield chemical plants missing in OSM)
        unmapped_rows = []
        for i in range(n_per_challenge):
            # Target is an industrial fire or flare, but OSM has no record -> dist = 999.0
            target = np.random.choice(["IND_ACCIDENT", "GAS_FLARE", "WILDFIRE"])
            is_accident = (target == "IND_ACCIDENT")
            unmapped_rows.append({
                "challenge_id": f"UNMAPPED_{i:04d}",
                "challenge_type": "Unmapped_Facility",
                "target_class": target,
                "frp_mean": float(np.random.uniform(60.0, 280.0) if is_accident else np.random.uniform(20.0, 80.0)),
                "frp_max": float(np.random.uniform(100.0, 450.0) if is_accident else np.random.uniform(35.0, 120.0)),
                "frp_trend": float(np.random.uniform(10.0, 35.0) if is_accident else np.random.uniform(-5.0, 5.0)),
                "dist_to_facility_km": 999.0, # Unmapped in GIS database
                "is_near_facility": 0.0,
                "area_ha": float(np.random.uniform(1.0, 6.0) if is_accident else (np.random.uniform(0.3, 1.2) if target == "GAS_FLARE" else np.random.uniform(15.0, 80.0))),
                "duration_hours": float(np.random.uniform(3.0, 24.0)),
                "frp_zscore": 0.0, # No facility baseline exists!
                "is_baseline_excursion": 0.0,
                "landcover_class": 3.0 if target != "WILDFIRE" else 1.0,
                "is_refinery": 0.0,
                "is_coal_mine": 0.0,
                "is_power_plant": 0.0,
                "compactness": float(np.random.uniform(0.65, 0.95) if target != "WILDFIRE" else np.random.uniform(0.1, 0.4)),
                "persistence_ratio": float(np.random.uniform(0.4, 0.8)),
                "spread_velocity": float(np.random.uniform(0.01, 0.15) if target != "WILDFIRE" else np.random.uniform(0.3, 1.5))
            })
        datasets["Unmapped_Facility"] = pd.DataFrame(unmapped_rows)

        # 4. Novel Facility Types (Pharmaceuticals, Fertilizer, Battery Storage)
        novel_rows = []
        for i in range(n_per_challenge):
            target = np.random.choice(["IND_ACCIDENT", "IND_NORMAL"])
            is_acc = (target == "IND_ACCIDENT")
            novel_rows.append({
                "challenge_id": f"NOVEL_{i:04d}",
                "challenge_type": "Novel_Facility_Type",
                "target_class": target,
                "frp_mean": float(np.random.uniform(70.0, 220.0) if is_acc else np.random.uniform(15.0, 45.0)),
                "frp_max": float(np.random.uniform(110.0, 380.0) if is_acc else np.random.uniform(20.0, 65.0)),
                "frp_trend": float(np.random.uniform(8.0, 28.0) if is_acc else np.random.uniform(-4.0, 4.0)),
                "dist_to_facility_km": float(np.random.uniform(0.1, 0.8)),
                "is_near_facility": 1.0,
                "area_ha": float(np.random.uniform(1.5, 8.0) if is_acc else np.random.uniform(0.5, 2.0)),
                "duration_hours": float(np.random.uniform(2.0, 36.0)),
                "frp_zscore": float(np.random.uniform(4.5, 11.0) if is_acc else np.random.uniform(0.2, 1.6)),
                "is_baseline_excursion": 1.0 if is_acc else 0.0,
                "landcover_class": 3.0,
                "is_refinery": 0.0, # Not a standard refinery
                "is_coal_mine": 0.0,
                "is_power_plant": 0.0,
                "compactness": float(np.random.uniform(0.5, 0.85)),
                "persistence_ratio": float(np.random.uniform(0.4, 0.9)),
                "spread_velocity": float(np.random.uniform(0.01, 0.2))
            })
        datasets["Novel_Facility_Type"] = pd.DataFrame(novel_rows)

        # 5. Catastrophic Extreme FRP (> 1000 MW)
        extreme_rows = []
        for i in range(n_per_challenge):
            target = np.random.choice(["IND_ACCIDENT", "WILDFIRE"])
            is_ind = (target == "IND_ACCIDENT")
            extreme_rows.append({
                "challenge_id": f"EXTREME_{i:04d}",
                "challenge_type": "Extreme_FRP_Outlier",
                "target_class": target,
                "frp_mean": float(np.random.uniform(400.0, 1200.0)),
                "frp_max": float(np.random.uniform(800.0, 2400.0)),
                "frp_trend": float(np.random.uniform(30.0, 120.0)),
                "dist_to_facility_km": float(np.random.uniform(0.05, 0.8) if is_ind else np.random.uniform(8.0, 50.0)),
                "is_near_facility": 1.0 if is_ind else 0.0,
                "area_ha": float(np.random.uniform(5.0, 25.0) if is_ind else np.random.uniform(80.0, 500.0)),
                "duration_hours": float(np.random.uniform(4.0, 72.0)),
                "frp_zscore": float(np.random.uniform(12.0, 35.0) if is_ind else 0.0),
                "is_baseline_excursion": 1.0 if is_ind else 0.0,
                "landcover_class": 3.0 if is_ind else 1.0,
                "is_refinery": 1.0 if is_ind else 0.0,
                "is_coal_mine": 0.0,
                "is_power_plant": 0.0,
                "compactness": float(np.random.uniform(0.4, 0.75) if is_ind else np.random.uniform(0.08, 0.25)),
                "persistence_ratio": float(np.random.uniform(0.6, 0.98)),
                "spread_velocity": float(np.random.uniform(0.05, 0.3) if is_ind else np.random.uniform(0.8, 3.5))
            })
        datasets["Extreme_FRP_Outlier"] = pd.DataFrame(extreme_rows)

        # 6. Wildfire Adjacency (Wildfire within 1 km of industrial refinery fence)
        wildfire_adj_rows = []
        for i in range(n_per_challenge):
            # Ground truth is WILDFIRE encroaching near refinery fence
            wildfire_adj_rows.append({
                "challenge_id": f"WF_ADJ_{i:04d}",
                "challenge_type": "Wildfire_Facility_Adjacency",
                "target_class": "WILDFIRE",
                "frp_mean": float(np.random.uniform(80.0, 350.0)),
                "frp_max": float(np.random.uniform(150.0, 600.0)),
                "frp_trend": float(np.random.uniform(10.0, 45.0)),
                "dist_to_facility_km": float(np.random.uniform(0.2, 1.4)), # Close proximity to refinery!
                "is_near_facility": 1.0,
                "area_ha": float(np.random.uniform(35.0, 180.0)), # Large perimeter
                "duration_hours": float(np.random.uniform(6.0, 48.0)),
                "frp_zscore": float(np.random.uniform(0.0, 1.5)), # Not an internal flare excursion
                "is_baseline_excursion": 0.0,
                "landcover_class": 1.0, # Forest / vegetation cover
                "is_refinery": 1.0, # Refinery is nearby
                "is_coal_mine": 0.0,
                "is_power_plant": 0.0,
                "compactness": float(np.random.uniform(0.12, 0.35)), # Non-compact irregular fire front
                "persistence_ratio": float(np.random.uniform(0.4, 0.8)),
                "spread_velocity": float(np.random.uniform(0.45, 1.8)) # High expansion velocity
            })
        datasets["Wildfire_Facility_Adjacency"] = pd.DataFrame(wildfire_adj_rows)

        return datasets

    @classmethod
    def evaluate_all(cls) -> Dict[str, Any]:
        ml_service = MLClassificationService()
        challenge_dfs = cls.generate_challenge_datasets()
        summary = {}

        os.makedirs("ml/evaluation", exist_ok=True)
        all_challenge_results = []

        print("=== THERMALIS-X RIGOROUS OPERATIONAL CHALLENGE BENCHMARKS ===")

        for name, df in challenge_dfs.items():
            correct = 0
            conformal_covered = 0
            abstained_count = 0
            reviewed_count = 0
            accepted_count = 0
            confidences = []
            entropies = []

            for _, row in df.iterrows():
                feats = {col: row[col] for col in DatasetBuilder.FEATURE_COLS}
                pred = ml_service.predict(feats)
                true_cls = row["target_class"]
                pred_cls = pred["source_class"]
                c_set = pred["conformal_prediction_set"]
                action = pred.get("decision_policy", {}).get("policy_action", "REVIEW")

                if pred_cls == true_cls:
                    correct += 1
                if true_cls in c_set:
                    conformal_covered += 1

                if action == "ABSTAIN":
                    abstained_count += 1
                elif action == "REVIEW":
                    reviewed_count += 1
                else:
                    accepted_count += 1

                confidences.append(pred["calibrated_prob"])
                entropies.append(pred["uncertainty"])

            n = len(df)
            raw_acc = float(correct / n)
            cov = float(conformal_covered / n)
            abstain_rate = float(abstained_count / n)
            review_rate = float(reviewed_count / n)
            accept_rate = float(accepted_count / n)
            mean_conf = float(np.mean(confidences))
            mean_ent = float(np.mean(entropies))

            summary[name] = {
                "samples": n,
                "raw_accuracy": round(raw_acc, 4),
                "conformal_coverage": round(cov, 4),
                "accept_rate": round(accept_rate, 4),
                "review_rate": round(review_rate, 4),
                "abstain_rate": round(abstain_rate, 4),
                "mean_calibrated_confidence": round(mean_conf, 4),
                "mean_entropy": round(mean_ent, 4)
            }

            all_challenge_results.append({
                "Challenge": name,
                "Samples": n,
                "Accuracy": f"{raw_acc*100:.1f}%",
                "Conformal_Cov": f"{cov*100:.1f}%",
                "Accept_Rate": f"{accept_rate*100:.1f}%",
                "Review_Rate": f"{review_rate*100:.1f}%",
                "Abstain_Rate": f"{abstain_rate*100:.1f}%",
                "Mean_Entropy": round(mean_ent, 3)
            })

            print(f"[{name}] Acc: {raw_acc*100:.1f}% | Conformal Cov: {cov*100:.1f}% | Abstain: {abstain_rate*100:.1f}% | Review: {review_rate*100:.1f}%")

        res_df = pd.DataFrame(all_challenge_results)
        res_df.to_csv("ml/evaluation/challenge_set_results.csv", index=False)
        with open("ml/evaluation/challenge_set_results.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        print("\nChallenge benchmark completed and saved to ml/evaluation/challenge_set_results.json")
        return summary

if __name__ == "__main__":
    ChallengeSetBenchmark.evaluate_all()
