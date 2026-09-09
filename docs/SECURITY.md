# THERMALIS-X Security Policy & Threat Mitigation

## Security Architecture Highlights
1. **Zero Hardcoded Secrets**: All credentials (NASA keys, JWT secrets, DB URLs) are loaded via environment variables and validated through Pydantic Settings.
2. **Role-Based Access Control (RBAC)**:
   - `VIEWER`: Read-only map and event inspection.
   - `ANALYST`: Ground truth verification, satellite optical tasking.
   - `SUPERVISOR`: Alert acknowledgment, emergency team dispatch.
   - `ADMIN`: Model promotion, system configuration, user management.
3. **Data Integrity & Idempotency**: Raw satellite observations are fingerprinted using SHA-256 (`raw_hash`). Re-transmissions cannot create duplicate observations or trigger redundant alerts.
4. **Adversarial Poisoning Defense**: Analyst feedback is quarantined and audited before being added to offline retraining sets, preventing single-user poisoning attacks.
