# THERMALIS-X Academic State of the Art & Research Gap

## Current Literature Limitations
1. **The Proximity Fallacy**: Early works (e.g., FIRMS-based automated alerting) equate spatial co-location with disaster status, ignoring continuous high-temperature manufacturing.
2. **Lack of Historical Baselines**: Existing systems evaluate single-pass hotspots in isolation without conditioning on the facility's long-term diurnal and seasonal thermal profile.
3. **Black-Box Overconfidence**: Most deep learning fire models output uncalibrated softmax scores without uncertainty quantification or abstention options.

## THERMALIS-X Scientific Contributions
1. Formalization of the 180-day robust Median Absolute Deviation (MAD) facility thermal baseline envelope.
2. Formulation of the 10-class thermal event taxonomy with zero circular labeling.
3. Multi-tier integration of ST-DBSCAN clustering, Platt-calibrated gradient boosting, and conformal abstention.
