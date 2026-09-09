# THERMALIS-X Relational Database Schema & Data Dictionary

The database follows a normalized relational structure with indexed spatial and temporal keys:

## Entity Relationship Overview
- `observations`: Individual satellite detections (lat, lon, acq_datetime, frp, brightness, confidence, raw_hash). Indexed on `(latitude, longitude, acq_datetime)`.
- `events`: Spatiotemporally aggregated thermal events (centroid_lat, centroid_lon, area_ha, max_frp, duration_hours, source_class, calibrated_prob, uncertainty, priority). Linked to `facilities`.
- `facilities`: Industrial facilities (name, facility_type, latitude, longitude, footprint_geojson, baseline_median_frp, baseline_mad_frp, baseline_p90_frp).
- `satellite_evidence`: Optical/SWIR scenes (event_id, sensor, scene_id, cloud_coverage, ndvi, nbr, status).
- `alerts`: Operational alerts (event_id, severity, priority_score, status, recommended_action).
- `analyst_feedback`: Human review records (event_id, analyst_id, verified_class, notes, evidence_reviewed_json).
- `audit_log`: System action records (actor, action, entity_type, entity_id, timestamp).
