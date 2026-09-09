# THERMALIS-X Scientific Reproducibility Protocol

To reproduce all benchmarks, models, and test fixtures from scratch:

```bash
# 1. Clone repository and install dependencies
git clone https://github.com/thermalis-x/thermalis.git
cd thermalis
pip install -r requirements.txt

# 2. Set PYTHONPATH to root
export PYTHONPATH=.   # Linux / macOS
$env:PYTHONPATH="."  # Windows PowerShell

# 3. Execute Automated Zero-Leakage Audit
python -m ml.evaluation.leakage_audit

# 4. Train XGBoost Model & Verify Cross-Validation Metrics
python -m ml.training.train_xgboost

# 5. Run Scientific Baseline Ladder Benchmark
python -m ml.training.train_baseline_ladder

# 6. Run Feature Ablation Study
python -m ml.evaluation.ablation_study

# 7. Execute Complete 17-Test Pytest Suite
pytest tests/ -v

# 8. Execute 15-Point Acceptance Test Suite
python scripts/run_acceptance_tests.py
```
Random seed `42` is fixed across all dataset generation, GroupKFold splits, and XGBoost training runs to guarantee deterministic reproduction down to floating-point precision.
