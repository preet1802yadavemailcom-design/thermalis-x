import pandas as pd
from ml.training.dataset_builder import DatasetBuilder
from sklearn.model_selection import GroupKFold
from sklearn.metrics import f1_score
from sklearn.ensemble import RandomForestClassifier

def run_ablation_study():
    df = DatasetBuilder.generate_synthetic_benchmark_data(n_samples=2000, random_seed=42)
    classes = DatasetBuilder.CLASSES
    class_to_idx = {c: i for i, c in enumerate(classes)}
    y = df["target_class"].map(class_to_idx).values
    groups = df["facility_id"].values

    all_feats = [
        "frp_mean", "frp_max", "frp_trend", "dist_to_facility_km",
        "is_near_facility", "area_ha", "duration_hours", "frp_zscore",
        "is_baseline_excursion", "landcover_class", "is_refinery",
        "is_coal_mine", "is_power_plant", "compactness",
        "persistence_ratio", "spread_velocity"
    ]

    gkf = GroupKFold(n_splits=5)
    train_idx, test_idx = next(gkf.split(df, y, groups=groups))

    # Full Model
    X = df[all_feats].values
    clf = RandomForestClassifier(n_estimators=60, random_state=42, max_depth=6)
    clf.fit(X[train_idx], y[train_idx])
    full_f1 = f1_score(y[test_idx], clf.predict(X[test_idx]), average="macro")

    ablations = [
        ("Without_Facility_Baseline", ["frp_zscore", "is_baseline_excursion"]),
        ("Without_Morphology", ["area_ha", "compactness", "spread_velocity"]),
        ("Without_Temporal", ["duration_hours", "persistence_ratio", "frp_trend"]),
        ("Without_Landcover", ["landcover_class"]),
        ("Without_Industrial_Context", ["is_refinery", "is_coal_mine", "is_power_plant", "dist_to_facility_km"])
    ]

    results = [{"Ablation": "Full_Model_All_Features", "Macro_F1": round(full_f1, 4), "Delta_F1": "0.0000"}]
    for name, dropped in ablations:
        kept = [f for f in all_feats if f not in dropped]
        X_abl = df[kept].values
        clf.fit(X_abl[train_idx], y[train_idx])
        abl_f1 = f1_score(y[test_idx], clf.predict(X_abl[test_idx]), average="macro")
        delta = abl_f1 - full_f1
        results.append({
            "Ablation": name,
            "Macro_F1": round(abl_f1, 4),
            "Delta_F1": f"{delta:+.4f}"
        })

    print("=== THERMALIS-X SCIENTIFIC FEATURE ABLATION STUDY ===")
    print(pd.DataFrame(results).to_string(index=False))

if __name__ == "__main__":
    run_ablation_study()
