import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from ml.training.dataset_builder import DatasetBuilder
from ml.training.train_xgboost import compute_ece

def evaluate_baseline_ladder():
    print("Loading benchmark dataset for Baseline Ladder evaluation...")
    df = pd.read_csv("data/processed/benchmark_dataset_v1.csv")
    classes = DatasetBuilder.CLASSES
    class_to_idx = {c: i for i, c in enumerate(classes)}
    y = df["target_class"].map(class_to_idx).values
    groups = df["facility_id"].values

    gkf = GroupKFold(n_splits=5)

    ladder_definitions = {
        "B0_FIRMS_Only": {
            "features": ["frp_mean", "frp_max"],
            "model_type": "random_forest"
        },
        "B1_FIRMS_Spatial": {
            "features": ["frp_mean", "frp_max", "dist_to_facility_km", "is_near_facility"],
            "model_type": "random_forest"
        },
        "B2_FIRMS_Landcover": {
            "features": ["frp_mean", "frp_max", "dist_to_facility_km", "is_near_facility", "landcover_class"],
            "model_type": "random_forest"
        },
        "B3_FIRMS_Temporal": {
            "features": ["frp_mean", "frp_max", "dist_to_facility_km", "duration_hours", "persistence_ratio"],
            "model_type": "random_forest"
        },
        "B4_FIRMS_Morphology": {
            "features": ["frp_mean", "frp_max", "dist_to_facility_km", "area_ha", "compactness", "spread_velocity"],
            "model_type": "random_forest"
        },
        "B5_FIRMS_Facility_Baseline": {
            "features": ["frp_mean", "frp_max", "dist_to_facility_km", "frp_zscore", "is_baseline_excursion"],
            "model_type": "random_forest"
        },
        "B6_Full_Multimodal_LogReg": {
            "features": DatasetBuilder.FEATURE_COLS,
            "model_type": "logistic_regression"
        },
        "B7_Full_Multimodal_RF": {
            "features": DatasetBuilder.FEATURE_COLS,
            "model_type": "random_forest"
        },
        "B8_Full_Multimodal_XGBoost": {
            "features": DatasetBuilder.FEATURE_COLS,
            "model_type": "xgboost"
        }
    }

    results = []

    for rung_name, cfg in ladder_definitions.items():
        feats = cfg["features"]
        mtype = cfg["model_type"]
        X = df[feats].values

        f1_folds = []
        prec_folds = []
        rec_folds = []
        ece_folds = []

        for fold, (tr_idx, val_idx) in enumerate(gkf.split(X, y, groups=groups)):
            X_tr, X_val = X[tr_idx], X[val_idx]
            y_tr, y_val = y[tr_idx], y[val_idx]

            if mtype == "logistic_regression":
                # Standardize for logistic regression
                mean = np.mean(X_tr, axis=0)
                std = np.std(X_tr, axis=0) + 1e-6
                X_tr_sc = (X_tr - mean) / std
                X_val_sc = (X_val - mean) / std
                clf = LogisticRegression(max_iter=1000, random_state=42 + fold)
                clf.fit(X_tr_sc, y_tr)
                probs = clf.predict_proba(X_val_sc)
            elif mtype == "random_forest":
                clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42 + fold, n_jobs=-1)
                clf.fit(X_tr, y_tr)
                probs = clf.predict_proba(X_val)
            elif mtype == "xgboost":
                clf = xgb.XGBClassifier(
                    n_estimators=120,
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
                probs = clf.predict_proba(X_val)

            preds = np.argmax(probs, axis=1)
            f1_folds.append(float(f1_score(y_val, preds, average="macro", zero_division=0)))
            prec_folds.append(float(precision_score(y_val, preds, average="macro", zero_division=0)))
            rec_folds.append(float(recall_score(y_val, preds, average="macro", zero_division=0)))
            ece_folds.append(compute_ece(probs, y_val))

        mean_f1 = float(np.mean(f1_folds))
        std_f1 = float(np.std(f1_folds))
        mean_prec = float(np.mean(prec_folds))
        mean_rec = float(np.mean(rec_folds))
        mean_ece = float(np.mean(ece_folds))

        print(f"[{rung_name}] Macro-F1: {mean_f1:.4f} +/- {std_f1:.4f} | Prec: {mean_prec:.4f} | Rec: {mean_rec:.4f} | ECE: {mean_ece:.4f}")

        results.append({
            "Rung": rung_name,
            "Model_Type": mtype,
            "Feature_Count": len(feats),
            "Mean_Macro_F1": round(mean_f1, 4),
            "Std_Macro_F1": round(std_f1, 4),
            "Mean_Precision": round(mean_prec, 4),
            "Mean_Recall": round(mean_rec, 4),
            "Mean_ECE": round(mean_ece, 4)
        })

    ladder_df = pd.DataFrame(results)
    os.makedirs("ml/evaluation", exist_ok=True)
    ladder_df.to_csv("ml/evaluation/baseline_ladder_results.csv", index=False)
    with open("ml/evaluation/baseline_ladder_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n=== THERMALIS-X SCIENTIFIC BASELINE LADDER 5-FOLD BENCHMARK SUMMARY ===")
    print(ladder_df.to_string(index=False))
    return ladder_df

if __name__ == "__main__":
    evaluate_baseline_ladder()
