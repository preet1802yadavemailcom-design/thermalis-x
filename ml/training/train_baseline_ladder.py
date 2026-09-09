import pandas as pd
import numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.ensemble import RandomForestClassifier
from ml.training.dataset_builder import DatasetBuilder

def evaluate_baseline_ladder():
    df = DatasetBuilder.generate_synthetic_benchmark_data(n_samples=2000, random_seed=42)
    classes = DatasetBuilder.CLASSES
    class_to_idx = {c: i for i, c in enumerate(classes)}
    y = df["target_class"].map(class_to_idx).values
    groups = df["facility_id"].values

    gkf = GroupKFold(n_splits=5)
    train_idx, test_idx = next(gkf.split(df, y, groups=groups))

    feature_sets = {
        "B0_FIRMS_Only": ["frp_mean", "frp_max"],
        "B1_FIRMS_Distance": ["frp_mean", "frp_max", "dist_to_facility_km", "is_near_facility"],
        "B2_FIRMS_Landcover": ["frp_mean", "frp_max", "dist_to_facility_km", "is_near_facility", "landcover_class"],
        "B3_FIRMS_Temporal": ["frp_mean", "frp_max", "dist_to_facility_km", "duration_hours", "persistence_ratio"],
        "B4_FIRMS_Morphology": ["frp_mean", "frp_max", "dist_to_facility_km", "area_ha", "compactness", "spread_velocity"],
        "B5_FIRMS_Facility_Baseline": ["frp_mean", "frp_max", "dist_to_facility_km", "frp_zscore", "is_baseline_excursion"],
        "B6_THERMALIS_Full_Multimodal": [
            "frp_mean", "frp_max", "frp_trend", "dist_to_facility_km",
            "is_near_facility", "area_ha", "duration_hours", "frp_zscore",
            "is_baseline_excursion", "landcover_class", "is_refinery",
            "is_coal_mine", "is_power_plant", "compactness",
            "persistence_ratio", "spread_velocity"
        ]
    }

    results = []
    for name, feats in feature_sets.items():
        X = df[feats].values
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        clf = RandomForestClassifier(n_estimators=60, random_state=42, max_depth=6)
        clf.fit(X_train, y_train)
        preds = clf.predict(X_test)

        macro_f1 = f1_score(y_test, preds, average="macro", zero_division=0)
        prec = precision_score(y_test, preds, average="macro", zero_division=0)
        rec = recall_score(y_test, preds, average="macro", zero_division=0)
        results.append({
            "Baseline": name,
            "Features_Count": len(feats),
            "Macro_F1": round(float(macro_f1), 4),
            "Precision": round(float(prec), 4),
            "Recall": round(float(rec), 4)
        })

    ladder_df = pd.DataFrame(results)
    print("=== THERMALIS-X SCIENTIFIC BASELINE LADDER BENCHMARK ===")
    print(ladder_df.to_string(index=False))
    return ladder_df

if __name__ == "__main__":
    evaluate_baseline_ladder()
