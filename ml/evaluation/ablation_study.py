import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.metrics import f1_score
import xgboost as xgb
from ml.training.dataset_builder import DatasetBuilder

def run_ablation_study():
    print("Loading benchmark dataset for scientific 5-fold Ablation Study...")
    df = pd.read_csv("data/processed/benchmark_dataset_v1.csv")
    classes = DatasetBuilder.CLASSES
    class_to_idx = {c: i for i, c in enumerate(classes)}
    y = df["target_class"].map(class_to_idx).values
    groups = df["facility_id"].values

    all_feats = DatasetBuilder.FEATURE_COLS

    gkf = GroupKFold(n_splits=5)

    ablations = [
        ("Full_Model_All_16_Features", []),
        ("Without_Facility_Baseline", ["frp_zscore", "is_baseline_excursion"]),
        ("Without_Morphology", ["area_ha", "compactness", "spread_velocity"]),
        ("Without_Temporal_Dynamics", ["duration_hours", "persistence_ratio", "frp_trend"]),
        ("Without_Landcover", ["landcover_class"]),
        ("Without_Industrial_Context", ["is_refinery", "is_coal_mine", "is_power_plant", "dist_to_facility_km", "is_near_facility"])
    ]

    results = []
    full_mean_f1 = None

    for name, dropped in ablations:
        kept = [f for f in all_feats if f not in dropped]
        X_sub = df[kept].values
        f1_folds = []

        for fold, (tr_idx, val_idx) in enumerate(gkf.split(X_sub, y, groups=groups)):
            X_tr, X_val = X_sub[tr_idx], X_sub[val_idx]
            y_tr, y_val = y[tr_idx], y[val_idx]

            clf = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.08,
                subsample=0.85,
                colsample_bytree=0.85,
                objective="multi:softprob",
                num_class=len(classes),
                random_state=42 + fold,
                eval_metric="mlogloss"
            )
            clf.fit(X_tr, y_tr)
            preds = clf.predict(X_val)
            f1_folds.append(float(f1_score(y_val, preds, average="macro", zero_division=0)))

        mean_f1 = float(np.mean(f1_folds))
        std_f1 = float(np.std(f1_folds))

        if full_mean_f1 is None:
            full_mean_f1 = mean_f1
            delta_f1 = 0.0
        else:
            delta_f1 = mean_f1 - full_mean_f1

        print(f"[{name}] Feats: {len(kept)} | Macro-F1: {mean_f1:.4f} +/- {std_f1:.4f} | Delta-F1: {delta_f1:+.4f}")

        results.append({
            "Ablation": name,
            "Features_Kept": len(kept),
            "Dropped_Features": dropped,
            "Mean_Macro_F1": round(mean_f1, 4),
            "Std_Macro_F1": round(std_f1, 4),
            "Delta_F1": round(delta_f1, 4)
        })

    abl_df = pd.DataFrame(results)
    os.makedirs("ml/evaluation", exist_ok=True)
    abl_df.to_csv("ml/evaluation/ablation_results.csv", index=False)
    with open("ml/evaluation/ablation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n=== THERMALIS-X SCIENTIFIC 5-FOLD FEATURE ABLATION STUDY ===")
    print(abl_df.to_string(index=False))
    return abl_df

if __name__ == "__main__":
    run_ablation_study()
