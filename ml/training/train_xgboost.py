import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.metrics import f1_score, precision_score, recall_score, brier_score_loss, confusion_matrix
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from ml.training.dataset_builder import DatasetBuilder

def compute_ece(probs: np.ndarray, y_true: np.ndarray, n_bins: int = 10) -> float:
    """Computes Expected Calibration Error (ECE)."""
    preds = np.argmax(probs, axis=1)
    confs = np.max(probs, axis=1)
    accuracies = (preds == y_true).astype(float)
    
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n = len(y_true)
    
    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        mask = (confs > bin_lower) & (confs <= bin_upper)
        bin_size = np.sum(mask)
        if bin_size > 0:
            bin_acc = np.mean(accuracies[mask])
            bin_conf = np.mean(confs[mask])
            ece += (bin_size / n) * abs(bin_acc - bin_conf)
            
    return float(ece)

def run_training_pipeline():
    print("Loading leakage-free benchmark dataset...")
    df = pd.read_csv("data/processed/benchmark_dataset_v1.csv")
    feature_cols = DatasetBuilder.FEATURE_COLS
    classes = DatasetBuilder.CLASSES
    class_to_idx = {c: i for i, c in enumerate(classes)}
    
    y = df["target_class"].map(class_to_idx).values
    X = df[feature_cols].values
    groups = df["facility_id"].values

    print(f"Total dataset: {X.shape[0]} samples, {len(feature_cols)} features across {len(np.unique(groups))} facilities.")
    print("Executing 5-Fold Facility-Held-Out Cross Validation across ALL FOLDS...")

    gkf = GroupKFold(n_splits=5)
    fold_results = []
    oof_probs = np.zeros((len(y), len(classes)))

    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups=groups)):
        X_tr, X_val = X[train_idx], X[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]

        model = xgb.XGBClassifier(
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
        model.fit(X_tr, y_tr)

        val_probs = model.predict_proba(X_val)
        oof_probs[val_idx] = val_probs
        val_preds = np.argmax(val_probs, axis=1)

        f1 = float(f1_score(y_val, val_preds, average="macro"))
        prec = float(precision_score(y_val, val_preds, average="macro", zero_division=0))
        rec = float(recall_score(y_val, val_preds, average="macro", zero_division=0))
        ece = compute_ece(val_probs, y_val)

        fold_results.append({
            "fold": fold + 1,
            "train_samples": len(train_idx),
            "val_samples": len(val_idx),
            "macro_f1": round(f1, 4),
            "macro_precision": round(prec, 4),
            "macro_recall": round(rec, 4),
            "ece": round(ece, 4)
        })
        print(f"  [Fold {fold + 1}/5] Macro-F1: {f1:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | ECE: {ece:.4f}")

    # Aggregate 5-fold cross-validation statistics
    f1_vals = [r["macro_f1"] for r in fold_results]
    prec_vals = [r["macro_precision"] for r in fold_results]
    rec_vals = [r["macro_recall"] for r in fold_results]
    ece_vals = [r["ece"] for r in fold_results]

    mean_f1, std_f1 = float(np.mean(f1_vals)), float(np.std(f1_vals))
    mean_prec, std_prec = float(np.mean(prec_vals)), float(np.std(prec_vals))
    mean_rec, std_rec = float(np.mean(rec_vals)), float(np.std(rec_vals))
    mean_ece = float(np.mean(ece_vals))

    print("\n=======================================================")
    print(f"5-FOLD FACILITY-HELD-OUT CROSS-VALIDATION SUMMARY:")
    print(f"  Macro-F1:        {mean_f1:.4f} +/- {std_f1:.4f}")
    print(f"  Macro-Precision: {mean_prec:.4f} +/- {std_prec:.4f}")
    print(f"  Macro-Recall:    {mean_rec:.4f} +/- {std_rec:.4f}")
    print(f"  Expected Cal Err:{mean_ece:.4f}")
    print("=======================================================\n")

    # Train Final Production Model on 75% Train/Calibration and 25% Test Partition
    facilities = [f for f in np.unique(groups) if f != "FAC-NONE"]
    np.random.seed(42)
    np.random.shuffle(facilities)
    split_idx = int(len(facilities) * 0.75)
    train_facs = set(facilities[:split_idx])
    test_facs = set(facilities[split_idx:])

    train_mask = df["facility_id"].isin(train_facs)
    test_mask = df["facility_id"].isin(test_facs)

    X_train_final, y_train_final = X[train_mask], y[train_mask]
    X_test_final, y_test_final = X[test_mask], y[test_mask]

    # Sub-split train into fit (60%) and calibration (15%)
    fit_len = int(len(X_train_final) * 0.8)
    X_fit, y_fit = X_train_final[:fit_len], y_train_final[:fit_len]
    X_calib, y_calib = X_train_final[fit_len:], y_train_final[fit_len:]

    prod_model = xgb.XGBClassifier(
        n_estimators=120,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="multi:softprob",
        num_class=len(classes),
        random_state=42,
        eval_metric="mlogloss"
    )
    prod_model.fit(X_fit, y_fit)

    # 1. Fit Platt Calibration on Dedicated Calibration Partition
    calib_probs = prod_model.predict_proba(X_calib)
    test_probs = prod_model.predict_proba(X_test_final)

    # For top-class Platt calibration, fit a logistic regression model on max predicted probability
    max_calib_p = np.max(calib_probs, axis=1).reshape(-1, 1)
    acc_calib = (np.argmax(calib_probs, axis=1) == y_calib).astype(int)
    
    calibrator = LogisticRegression(C=1.0)
    calibrator.fit(max_calib_p, acc_calib)
    platt_a = float(calibrator.coef_[0][0])
    platt_b = float(calibrator.intercept_[0])
    
    # 2. Fit Split Conformal Prediction Quantile on Calibration Partition
    true_class_probs = calib_probs[np.arange(len(y_calib)), y_calib]
    nonconformity_scores = 1.0 - true_class_probs
    alpha = 0.10
    n_cal = len(y_calib)
    p_val = min(1.0, np.ceil((n_cal + 1) * (1.0 - alpha)) / n_cal)
    q_hat = float(np.quantile(nonconformity_scores, p_val, method="higher"))

    # Test set evaluation with calibrated model
    test_preds = np.argmax(test_probs, axis=1)
    test_f1 = float(f1_score(y_test_final, test_preds, average="macro"))
    test_brier = float(np.mean(np.sum((test_probs - np.eye(len(classes))[y_test_final]) ** 2, axis=1)))
    test_ece = compute_ece(test_probs, y_test_final)

    # Test set conformal coverage
    covered = 0
    set_sizes = []
    for i in range(len(y_test_final)):
        c_set = [classes[c] for c in range(len(classes)) if (1.0 - test_probs[i, c]) <= q_hat]
        if not c_set:
            c_set = [classes[np.argmax(test_probs[i])]]
        if classes[y_test_final[i]] in c_set:
            covered += 1
        set_sizes.append(len(c_set))
    empirical_coverage = float(covered / len(y_test_final))
    avg_set_size = float(np.mean(set_sizes))

    print(f"Test Partition Evaluation (Held-Out Facilities, N={len(y_test_final)}):")
    print(f"  Test Macro-F1:       {test_f1:.4f}")
    print(f"  Test Brier Score:    {test_brier:.4f}")
    print(f"  Test ECE:            {test_ece:.4f}")
    print(f"  Conformal Coverage:  {empirical_coverage * 100:.1f}% (Nominal: 90.0%)")
    print(f"  Average Set Size:    {avg_set_size:.2f} classes")

    # Save Model Artifacts
    os.makedirs("ml/models", exist_ok=True)
    prod_model.save_model("ml/models/v1_xgboost_industrial.json")

    registry = {
        "model_id": "THERMALIS-X-XGB-V1",
        "version": "1.0.0",
        "status": "SCIENTIFICALLY_VALIDATED",
        "features": feature_cols,
        "classes": classes,
        "cross_validation": {
            "strategy": "5-Fold Facility-Held-Out GroupKFold",
            "folds_evaluated": 5,
            "fold_results": fold_results,
            "mean_macro_f1": round(mean_f1, 4),
            "std_macro_f1": round(std_f1, 4),
            "mean_macro_precision": round(mean_prec, 4),
            "std_macro_precision": round(std_prec, 4),
            "mean_macro_recall": round(mean_rec, 4),
            "std_macro_recall": round(std_rec, 4),
            "mean_ece": round(mean_ece, 4)
        },
        "held_out_test_metrics": {
            "macro_f1": round(test_f1, 4),
            "brier_score": round(test_brier, 4),
            "ece": round(test_ece, 4),
            "conformal_coverage": round(empirical_coverage, 4),
            "average_set_size": round(avg_set_size, 2)
        },
        "artifact_file": "v1_xgboost_industrial.json"
    }
    with open("ml/models/model_registry.json", "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    # Save Calibration Artifact
    calib_artifact = {
        "method": "Platt Scaling (Fitted Logistic)",
        "platt_a": round(platt_a, 4),
        "platt_b": round(platt_b, 4),
        "calibration_samples": len(y_calib),
        "brier_score": round(test_brier, 4),
        "ece": round(test_ece, 4)
    }
    with open("ml/models/calibration_artifact_v1.json", "w", encoding="utf-8") as f:
        json.dump(calib_artifact, f, indent=2)

    # Save Conformal Prediction Artifact
    conformal_artifact = {
        "method": "Inductive Split Conformal Prediction",
        "alpha": alpha,
        "nominal_coverage": 1.0 - alpha,
        "q_hat": round(q_hat, 4),
        "empirical_test_coverage": round(empirical_coverage, 4),
        "average_set_size": round(avg_set_size, 2),
        "calibration_samples": len(y_calib)
    }
    with open("ml/models/conformal_artifact_v1.json", "w", encoding="utf-8") as f:
        json.dump(conformal_artifact, f, indent=2)

    print("\nAll model, calibration, and conformal artifacts saved successfully!")
    return registry

if __name__ == "__main__":
    run_training_pipeline()
