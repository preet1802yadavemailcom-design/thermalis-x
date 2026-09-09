# THERMALIS-X STRIDE Threat Model

| Threat Category | Attack Vector | System Vulnerability | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Adversary injects forged satellite telemetry into FIRMS endpoint. | Unauthenticated API ingestion. | HMAC signature validation and NASA source certificate verification. |
| **Tampering** | Rogue actor modifies facility baseline to mask unauthorized emissions. | Unaudited database updates. | Immutable historical observation logging and cryptographically signed audit logs. |
| **Repudiation** | Analyst dismisses a true emergency fire and denies action. | Lack of accountability. | Every analyst verification requires JWT identity and is permanently written to `analyst_feedback` and `audit_log`. |
| **Information Disclosure** | Leakage of critical infrastructure vulnerability details. | Public exposure of industrial facility coordinates. | Sensitive facility parameters restricted to authorized roles (`ANALYST`, `SUPERVISOR`). |
| **Denial of Service** | Flooding backend with synthetic observations. | Resource exhaustion. | Rate limiting via `slowapi` and spatial bounding box screening. |
| **Elevation of Privilege** | Guest user submits emergency dispatch alerts. | Missing RBAC enforcement. | Declarative FastAPI role dependencies (`require_role("SUPERVISOR")`). |
