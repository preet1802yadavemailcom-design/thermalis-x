# THERMALIS-X Model Card (Mitchell et al. Guidelines)

## 1. Model Details
- **Architecture**: Calibrated Gradient Boosted Decision Tree (XGBoost 3.3.0).
- **Objective Function**: Multi-class softprob ($10$ output classes).
- **Hyperparameters**: $100$ estimators, learning rate $0.08$, max depth $5$, subsample $0.85$.
- **Calibration**: Post-hoc Platt Sigmoid Scaling on class likelihoods.
- **Uncertainty Layer**: Normalized Shannon Entropy with margin-based conformal abstention ($H > 0.60$ or $\Delta P < 0.15$).

## 2. Performance Metrics (Facility-Held-Out Validation)
- **Macro-F1 Score**: 0.9939
- **Macro-Precision**: 0.9939
- **Macro-Recall**: 0.9941
- **Calibration Brier Score**: 0.0124 (indicating high reliability)

## 3. Intended Use & Limitations
- **Intended Use**: Real-time decision support for industrial disaster management authorities, fire brigades, and environmental regulators.
- **Prohibited Use**: Autonomous trigger of irreversible explosive suppression systems without human analyst confirmation.
- **Remote Sensing Limitations**: Heavy monsoon cloud cover can attenuate thermal infrared radiance. In cloudy conditions, THERMALIS-X broadens uncertainty bounds and triggers abstention.
