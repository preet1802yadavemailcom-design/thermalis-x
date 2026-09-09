# THERMALIS-X Systematic Experiment Registry

| Experiment ID | Hypothesis | Features Tested | Model Architecture | Metric (Macro-F1) | Decision / Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-001** | Heuristic FIRMS-only rule fails to separate flares from fires. | `frp_mean`, `frp_max` | Rule Heuristic | 0.5176 | Baseline established. High false alarm rate confirmed. |
| **EXP-002** | Adding facility distance improves precision but confuses flares. | FRP + Distance | Random Forest | 0.8613 | Confirms proximity alone cannot separate normal flare from accident. |
| **EXP-003** | Adding ESA landcover separates agricultural burns from industrial. | FRP + Dist + Landcover | Random Forest | 0.9181 | Major reduction in rural crop burn false alarms. |
| **EXP-004** | Adding event morphology (area, compactness) separates point flares. | FRP + Dist + Morphology | Random Forest | 0.9600 | Compactness cleanly isolates stationary flare stacks. |
| **EXP-005** | Adding facility MAD baseline detects true accidents. | Full Feature Set | XGBoost Classifier | **0.9939** | Production model approved. Zero-leakage verified. |
