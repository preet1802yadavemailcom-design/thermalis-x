# THERMALIS-X Red-Team Adversarial Audit Report

| Attack Scenario | Threat Vector | Expected Behavior | Actual Behavior | Severity | Mitigation & Fix Status |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Refinery Flare Spikes During Routine Maintenance** | High FRP point source at HPCL Vizag. | Differentiate from fire if within spatial footprint. | Correctly identified as GAS_FLARE due to zero perimeter dilation ($0.4\text{ ha}$) and high compactness. | HIGH | **MITIGATED & VERIFIED** |
| **Wildfire Adjacent to Industrial Park** | Forest fire 1.5 km from factory boundary. | Avoid falsely blaming factory. | Identified as WILDFIRE due to high spread velocity ($>0.5\text{ km/h}$) and forest landcover. | HIGH | **MITIGATED & VERIFIED** |
| **Monsoon Cloud Masking Thermal Peak** | Optical bands 100% obscured by monsoonal clouds. | Do not declare 'No Fire' when evidence is missing. | System enters `CLOUDY_OPTICAL_DEGRADED` state, broadens uncertainty, and tasks radar/SAR. | HIGH | **MITIGATED & VERIFIED** |
| **Unregistered Chemical Plant (Missing in OSM)** | Fire at new factory without OSM tag. | Graceful fallback using landcover and morphology. | Identified as high-consequence thermal anomaly via FRP surge and industrial spectral indices. | MEDIUM | **MITIGATED & VERIFIED** |
| **Synthetic Observation Spoofing via API** | Attacker injects forged FIRMS coordinates. | Quarantine out-of-bounds or duplicate data. | Validator enforces latitude [-90, 90], longitude [-180, 180], FRP < 15,000 MW, and SHA256 idempotency. | CRITICAL | **MITIGATED & VERIFIED** |
| **Analyst Ground-Truth Retraining Poisoning** | Malicious insider overrides true disasters. | Quarantine raw feedback from production retraining. | Feedback quarantined in separate table; requires supervisor audit before offline dataset ingestion. | HIGH | **MITIGATED & VERIFIED** |
