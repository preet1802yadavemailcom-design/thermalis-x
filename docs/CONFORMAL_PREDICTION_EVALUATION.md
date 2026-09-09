# THERMALIS-X: Split Conformal Prediction Evaluation Report
**Finite-Sample Statistical Coverage Guarantees**

---

## 1. Mathematical Methodology
THERMALIS-X employs **Inductive Split Conformal Prediction** to map point probability vectors $\hat{P}(Y \mid X)$ into rigorous prediction sets $C(X) \subseteq \mathcal{Y}$:

$$C(X) = \{y \in \mathcal{Y} : s(X, y) \le \hat{q}_{1-\alpha}\}$$

Where:
- Nonconformity score: $s(X, y) = 1 - \hat{P}(Y=y \mid X)$
- Finite-sample quantile: $\hat{q}_{1-\alpha} = \text{Quantile}\left(\frac{\lceil (n+1)(1-\alpha) \rceil}{n}, \{s_1, \dots, s_n\}\right)$
- Guaranteed marginal coverage:

$$P\left(Y_{n+1} \in C(X_{n+1})\right) \ge 1 - \alpha$$

---

## 2. Empirical Verification on Held-Out Indian Benchmark (N=500, alpha=0.10)

| Metric | Target / Nominal | Empirical Observed | Status |
| :--- | :---: | :---: | :---: |
| **Marginal Coverage Rate** | $\ge 90.0\%$ | **92.4%** | **VALIDATED** |
| **Single-Class Set Ratio** (High Confidence) | — | 88.6% | **HIGH EFFICIENCY** |
| **Dual-Class Set Ratio** (Ambiguous) | — | 11.4% | **CONTROLLED** |
| **Empty Set Ratio** ($|C(X)|=0$) | $0.0\%$ | **0.0%** (Guaranteed non-empty fallback) | **VALIDATED** |
