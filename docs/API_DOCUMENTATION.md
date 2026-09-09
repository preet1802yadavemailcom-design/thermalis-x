# THERMALIS-X REST API Specifications (OpenAPI 3.0)

Base URL: `http://localhost:8000/api/v1`

## Key Endpoints

### 1. Health & Dependency Status
- `GET /health`: Returns system state (`READY`, `DEGRADED`), app version, and sub-component status (Database, FIRMS Connector, Element84 STAC, Open-Meteo, XGBoost).

### 2. Thermal Events
- `GET /events`: Lists monitored events with query filters:
  - `status`: `ACTIVE`, `TERMINATED`, `MERGED`, `SPLIT`
  - `priority`: `INFORMATIONAL`, `WATCH`, `WARNING`, `CRITICAL`
  - `source_class`: `IND_ACCIDENT`, `GAS_FLARE`, etc.
  - `min_frp`: Filter by minimum fire radiative power (MW).
- `GET /events/{id}`: Returns complete event diagnostics including convex hull geometry, calibrated probabilities, uncertainty entropy, and SHAP explanation.
- `GET /events/{id}/timeline`: Returns chronological satellite observation history.

### 3. Industrial Facilities & Baselines
- `GET /facilities`: Lists all registered industrial facilities, boundary footprints, and 180-day baseline statistics ($P_{10}, P_{90}, \text{median}, \text{MAD}$).
- `GET /facilities/{id}`: Returns detailed facility profile and operational thresholds.

### 4. Alerts & Operational Escalations
- `GET /alerts`: Returns operational alert feed.
- `POST /alerts/{id}/acknowledge`: Acknowledges alert with analyst notes.

### 5. Historical Replay Engine
- `GET /replay/cases`: Lists the 3 Indian case studies (HPCL Vizag, Jharia Coalfields, Morbi Ceramics).
- `GET /replay/cases/{case_id}/steps`: Step-by-step telemetry sequence for presentation playback.

### 6. Human-in-the-Loop Feedback
- `POST /feedback`: Records analyst confirmation or classification override with review audit trail.
