# THERMALIS-X Defensible Answers to 25 Skeptical Jury Inquiries

### Q1: Why use AI? Isn't a simple distance threshold enough?
**A**: A distance threshold fails catastrophically in real-world remote sensing. An oil refinery continuously flares gas within its perimeter. A distance rule labels that flare as an active fire every single day. AI evaluates multi-dimensional spatiotemporal physics: FRP slope, temporal persistence, landcover fuel loading, perimeter dilation, and baseline excursion z-scores.

### Q2: Why XGBoost rather than a deep Transformer or GNN?
**A**: Satellite thermal swaths arrive at discrete, non-uniform intervals (typically 2 to 4 passes per day per region). Deep temporal Transformers require uniform time-series grids and overfit on tabular geospatial features. XGBoost natively handles missing modalities, trains in seconds, achieves 0.9939 Macro-F1 under strict facility-held-out validation, and provides exact, mathematically rigorous TreeSHAP feature attributions.

### Q3: How do you prevent spatial data leakage during evaluation?
**A**: We implement strict Facility-Held-Out GroupKFold validation. No facility in the test partition ever appears in the training partition. The model is tested exclusively on unseen industrial complexes, proving genuine inductive generalization.

### Q4: What happens if NASA FIRMS is down or rate-limited?
**A**: THERMALIS-X operates with zero-failure graceful degradation. If FIRMS is unreachable, the system transparently serves cached telemetry, raises a visible degraded status banner, and enables offline Historical Replay mode.
