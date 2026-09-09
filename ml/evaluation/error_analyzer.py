import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from collections import defaultdict
from sklearn.metrics import confusion_matrix, classification_report
from backend.app.services.ml_service import MLClassificationService
from ml.training.dataset_builder import DatasetBuilder

class ErrorAnalyzer:
    """
    Forensic Failure and Error Analysis Engine.
    Evaluates real benchmark events against the trained model, parses genuine confusion pairs,
    and groups failures into domain-grounded root-cause buckets.
    """
    BUCKETS = [
        "abstained_high_uncertainty",
        "flare_misclassified_as_accident",
        "accident_misclassified_as_flare",
        "wildfire_near_industry_misclassified_as_accident",
        "crop_burn_misclassified_as_wildfire",
        "industrial_normal_misclassified_as_accident",
        "subsurface_coal_fire_ambiguity",
        "other_confusion"
    ]

    @classmethod
    def analyze_errors(cls, dataset_path: str = "data/processed/benchmark_dataset_v1.csv") -> Dict[str, Any]:
        print("Loading dataset for real forensic error analysis...")
        df = pd.read_csv(dataset_path)
        ml_service = MLClassificationService()

        classes = DatasetBuilder.CLASSES
        class_to_idx = {c: i for i, c in enumerate(classes)}

        total_samples = len(df)
        y_true = []
        y_pred = []
        errors = []
        bucket_counts = defaultdict(int)

        for idx, row in df.iterrows():
            feats = {c: row[c] for c in DatasetBuilder.FEATURE_COLS}
            pred = ml_service.predict(feats)
            
            true_label = row["target_class"]
            pred_label = pred["source_class"]
            y_true.append(true_label)
            y_pred.append(pred_label)

            if true_label != pred_label:
                # Classify into specific forensic failure bucket
                if pred_label == "UNCERTAIN" and pred["abstained"]:
                    b = "abstained_high_uncertainty"
                elif true_label == "GAS_FLARE" and pred_label == "IND_ACCIDENT":
                    b = "flare_misclassified_as_accident"
                elif true_label == "IND_ACCIDENT" and pred_label == "GAS_FLARE":
                    b = "accident_misclassified_as_flare"
                elif true_label == "WILDFIRE" and pred_label == "IND_ACCIDENT":
                    b = "wildfire_near_industry_misclassified_as_accident"
                elif true_label == "AGRI_BURN" and pred_label == "WILDFIRE":
                    b = "crop_burn_misclassified_as_wildfire"
                elif true_label == "IND_NORMAL" and pred_label == "IND_ACCIDENT":
                    b = "industrial_normal_misclassified_as_accident"
                elif true_label == "MINE_HEAT" and pred_label in ["IND_NORMAL", "OTHER_NATURAL"]:
                    b = "subsurface_coal_fire_ambiguity"
                else:
                    b = "other_confusion"

                bucket_counts[b] += 1

                errors.append({
                    "sample_id": int(row.get("sample_id", idx)),
                    "facility_id": str(row.get("facility_id", "UNKNOWN")),
                    "true_class": true_label,
                    "predicted_class": pred_label,
                    "calibrated_confidence": pred["calibrated_prob"],
                    "entropy": pred["uncertainty"],
                    "margin": pred["margin"],
                    "abstained": pred["abstained"],
                    "conformal_set": pred["conformal_prediction_set"],
                    "decision_action": pred.get("decision_policy", {}).get("policy_action", "UNKNOWN"),
                    "failure_bucket": b,
                    "key_features": {
                        "frp_max": round(float(row["frp_max"]), 1),
                        "frp_zscore": round(float(row["frp_zscore"]), 2),
                        "dist_to_facility_km": round(float(row["dist_to_facility_km"]), 2),
                        "compactness": round(float(row["compactness"]), 2),
                        "spread_velocity": round(float(row["spread_velocity"]), 3)
                    }
                })

        error_rate = len(errors) / total_samples
        
        # Calculate full confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=classes)
        cm_dict = {}
        for i, c_true in enumerate(classes):
            cm_dict[c_true] = {classes[j]: int(cm[i, j]) for j in range(len(classes))}

        report = {
            "total_samples": total_samples,
            "total_errors": len(errors),
            "error_rate_pct": round(error_rate * 100, 2),
            "accuracy_pct": round((1.0 - error_rate) * 100, 2),
            "bucket_distribution": {b: bucket_counts[b] for b in cls.BUCKETS},
            "sample_misclassifications": errors[:25], # Inspect first 25 concrete cases
            "confusion_matrix": cm_dict,
            "mitigation_analysis": {
                "uncertainty_abstained_errors": sum(1 for e in errors if e["abstained"] or e["decision_action"] in ["ABSTAIN", "REVIEW"]),
                "effective_safety_net_pct": round(
                    sum(1 for e in errors if e["abstained"] or e["decision_action"] in ["ABSTAIN", "REVIEW"]) / max(1, len(errors)) * 100, 2
                )
            }
        }

        os.makedirs("ml/evaluation", exist_ok=True)
        with open("ml/evaluation/error_analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print("=== THERMALIS-X FORENSIC ERROR ANALYSIS SUMMARY ===")
        print(f"Total Samples: {total_samples} | Errors: {len(errors)} | Error Rate: {report['error_rate_pct']}%")
        print("Failure Buckets:")
        for b, count in report["bucket_distribution"].items():
            print(f"  {b}: {count}")
        print(f"Safety Net Mitigation: {report['mitigation_analysis']['effective_safety_net_pct']}% of errors were flagged for REVIEW or ABSTAINED by conformal policy!")
        
        return report

if __name__ == "__main__":
    ErrorAnalyzer.analyze_errors()
