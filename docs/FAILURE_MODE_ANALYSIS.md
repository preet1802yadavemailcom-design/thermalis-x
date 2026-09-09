# THERMALIS-X Failure Mode and Effects Analysis (FMEA)

| Failure Mode | Cause | System Impact | Severity | Autonomous Mitigation | Fallback State |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NASA FIRMS API Outage** | NASA server downtime or network disconnect. | Live observation stream pauses. | High | System serves cached telemetry and switches to Historical Replay mode. | Degraded live mode with visible dashboard warning banner. |
| **Cloud Obscuration** | Dense monsoon cloud cover masks thermal infrared emission. | Underestimated FRP or missed detection. | Medium | Cloud fraction checked via STAC metadata; uncertainty interval broadened; triggers abstention. | `CLOUDY_OPTICAL_DEGRADED` evidence state. |
| **OSM Facility Data Incomplete** | Unregistered or new chemical plant missing in OSM. | Proximity distance defaults to large value. | Medium | Landcover classification, FRP slope, and event morphology detect industrial signature; flags `UNINDEXED_INDUSTRIAL_SUSPECT`. | Context-aware fallback. |
| **Model Ingestion Drift** | Sensor degradation on aging satellite platform. | Shift in input feature distributions. | Medium | Model output calibrated with Platt scaling; Shannon entropy detects high uncertainty and abstains. | Human analyst mandatory verification. |
