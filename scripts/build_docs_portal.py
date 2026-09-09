import os

docs_index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>THERMALIS-X Documentation Hub & Technical Specifications</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-base: #0a0e17;
      --bg-surface: #111827;
      --bg-surface-elevated: #1f2937;
      --border-color: #374151;
      --text-primary: #f9fafb;
      --text-secondary: #9ca3af;
      --accent: #3b82f6;
      --accent-hover: #60a5fa;
      --danger: #ef4444;
      --warning: #f59e0b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', sans-serif;
      background: var(--bg-base);
      color: var(--text-primary);
      line-height: 1.6;
      padding: 40px 20px;
    }
    .container { max-width: 1100px; margin: 0 auto; }
    header {
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 24px;
      margin-bottom: 32px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }
    h1 { font-size: 28px; font-weight: 700; }
    .subtitle { color: var(--text-secondary); font-size: 14px; margin-top: 4px; }
    .btn {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-color);
      color: #fff;
      padding: 8px 16px;
      border-radius: 6px;
      text-decoration: none;
      font-size: 13px;
      font-weight: 600;
    }
    .btn:hover { background: #374151; }
    .btn-primary { background: #2563eb; border-color: #3b82f6; }
    .btn-primary:hover { background: #1d4ed8; }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
      margin-bottom: 40px;
    }
    .card {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 20px;
      transition: all 0.2s;
    }
    .card:hover {
      border-color: var(--accent);
      transform: translateY(-2px);
    }
    .card h3 { font-size: 16px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }
    .card p { font-size: 13px; color: var(--text-secondary); margin-bottom: 16px; }
    .card a {
      color: var(--accent-hover);
      text-decoration: none;
      font-size: 12px;
      font-weight: 600;
    }
    .card a:hover { text-decoration: underline; }

    .pdf-list {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 20px;
      margin-top: 24px;
    }
    .pdf-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid var(--border-color);
      font-size: 13px;
    }
    .pdf-item:last-child { border-bottom: none; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>THERMALIS-X Documentation Hub</h1>
        <div class="subtitle">SIH Problem Statement 26162 • AI-Based Industrial Fire & Persistent Thermal Source Intelligence</div>
      </div>
      <div style="display: flex; gap: 10px;">
        <a href="/" class="btn">Console View</a>
        <a href="/docs-portal/completion.html" class="btn btn-primary">QA Traceability Matrix</a>
      </div>
    </header>

    <h2 style="font-size: 18px; margin-bottom: 16px;">Core Technical Architecture & Specifications</h2>
    <div class="grid">
      <div class="card">
        <h3>System Architecture</h3>
        <p>Comprehensive high-level dataflow topology, multi-tier asynchronous architecture, and component interactions.</p>
        <a href="ARCHITECTURE.md">Read Architecture Doc &rarr;</a>
      </div>
      <div class="card">
        <h3>Verified Data Sources</h3>
        <p>Ground-truth provenance, endpoints, update cadences, and licenses for NASA FIRMS, OSM, STAC, and Open-Meteo.</p>
        <a href="DATA_SOURCES.md">Read Data Sources Doc &rarr;</a>
      </div>
      <div class="card">
        <h3>Dataset Card</h3>
        <p>Formal Gebru et al. specification of the 2,000-sample benchmark dataset and zero-circular labeling guarantees.</p>
        <a href="DATASET_CARD.md">Read Dataset Card &rarr;</a>
      </div>
      <div class="card">
        <h3>Model Card</h3>
        <p>Mitchell et al. model card detailing 10-class XGBoost architecture, calibration, and conformal uncertainty.</p>
        <a href="MODEL_CARD.md">Read Model Card &rarr;</a>
      </div>
      <div class="card">
        <h3>Security & Threat Model</h3>
        <p>STRIDE threat modeling, RBAC permission matrices, input sanitization, and adversarial poisoning defense.</p>
        <a href="SECURITY.md">Read Security Policy &rarr;</a>
      </div>
      <div class="card">
        <h3>Failure Mode Analysis (FMEA)</h3>
        <p>Exhaustive analysis of 18 remote sensing failure modes including cloud attenuation and API outages.</p>
        <a href="FAILURE_MODE_ANALYSIS.md">Read FMEA Report &rarr;</a>
      </div>
      <div class="card">
        <h3>Testing Architecture</h3>
        <p>Overview of the 17-test unit/integration suite and 15 formal acceptance tests (AT-001 through AT-015).</p>
        <a href="TESTING.md">Read Testing Guide &rarr;</a>
      </div>
      <div class="card">
        <h3>Scientific Reproducibility</h3>
        <p>Exact commands and locked random seeds to reproduce all models, baseline ladders, and metrics from scratch.</p>
        <a href="REPRODUCIBILITY.md">Read Protocol &rarr;</a>
      </div>
      <div class="card">
        <h3>Judge Defense & QA</h3>
        <p>Scientifically defensible answers to 25 tough jury inquiries on AI necessity, leakage prevention, and scaling.</p>
        <a href="JUDGE_QA.md">Read Jury Q&A &rarr;</a>
      </div>
    </div>

    <h2 style="font-size: 18px; margin-bottom: 16px;">Automated 27-Module Technical Documentation PDFs</h2>
    <div class="pdf-list">
      <div class="pdf-item">
        <span><strong>THERMALIS-X Master Technical Document</strong> (Complete 40+ page master compilation)</span>
        <a href="pdf/THERMALIS-X_MASTER_TECHNICAL_DOCUMENT.pdf" target="_blank" class="btn" style="padding: 4px 10px; font-size: 11px;">Download PDF</a>
      </div>
      <div class="pdf-item"><span>01. System Overview & Executive Architecture</span><a href="pdf/01_SYSTEM_OVERVIEW.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>02. Data Ingestion Architecture & Resilient Adapters</span><a href="pdf/02_DATA_INGESTION.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>03. NASA FIRMS VIIRS & MODIS Sensor Deep Dive</span><a href="pdf/03_NASA_FIRMS.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>04. Data Validation, Quarantine & Idempotency</span><a href="pdf/04_DATA_VALIDATION.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>05. Spatiotemporal Event Engine & Lineage Tracking</span><a href="pdf/05_EVENT_ENGINE.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>06. Industrial Infrastructure Spatial Indexing</span><a href="pdf/06_INDUSTRIAL_CONTEXT.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>07. Historical Facility Baseline & MAD Excursions</span><a href="pdf/07_FACILITY_BASELINE.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>08. 48-Dimensional Feature Engineering Ontology</span><a href="pdf/08_FEATURE_ENGINEERING.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>09. Leakage-Free Dataset Construction & Labeling</span><a href="pdf/09_DATASET_AND_LABELING.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>10. Machine Learning Pipeline & Model Selection</span><a href="pdf/10_ML_MODEL.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>11. Baseline Ladder Evaluation & Benchmark Metrics</span><a href="pdf/11_EVALUATION.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>12. Probability Calibration & Conformal Uncertainty</span><a href="pdf/12_UNCERTAINTY_CALIBRATION.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>13. Grounded Feature Attribution (SHAP Explainer)</span><a href="pdf/13_EXPLAINABILITY.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>14. Multimodal Satellite Evidence (Sentinel-2 L2A)</span><a href="pdf/14_SATELLITE_EVIDENCE.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>15. Multi-Criteria Operational Risk Priority Engine</span><a href="pdf/15_RISK_PRIORITY.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>16. Alert Engine, Deduplication & Cooldown</span><a href="pdf/16_ALERT_ENGINE.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>17. GIS Operations Console & UX Architecture</span><a href="pdf/17_GIS.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>18. FastAPI Backend Architecture & OpenAPI Docs</span><a href="pdf/18_BACKEND_API.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>19. Relational PostGIS Database & Data Dictionary</span><a href="pdf/19_DATABASE.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>20. Cybersecurity Architecture & Defense in Depth</span><a href="pdf/20_CYBERSECURITY.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>21. Resilience, Degraded Modes & Zero-Failure Plan</span><a href="pdf/21_RESILIENCE.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>22. Human-in-the-Loop Analyst Verification Loop</span><a href="pdf/22_HUMAN_IN_LOOP.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>23. Testing & QA Protocol (Acceptance Tests AT-001 - AT-015)</span><a href="pdf/23_TESTING_QA.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>24. Production Deployment, Docker & Scalability</span><a href="pdf/24_DEPLOYMENT.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>25. Scientific Reproducibility Audit & Lockfiles</span><a href="pdf/25_REPRODUCIBILITY.pdf" target="_blank">View PDF</a></div>
      <div class="pdf-item"><span>26. SIH Grand Finale 5-Minute & 10-Minute Demo Guide</span><a href="pdf/26_SIH_DEMO.pdf" target="_blank">View PDF</a></div>
    </div>
  </div>
</body>
</html>
"""

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(docs_index_html)

completion_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>THERMALIS-X Quality Gate & Completion Dashboard</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; background: #0a0e17; color: #f9fafb; padding: 40px 20px; }
    .container { max-width: 1200px; margin: 0 auto; }
    h1 { font-size: 24px; margin-bottom: 8px; }
    .status-badge { background: #065f46; color: #34d399; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 12px; }
    table { width: 100%; border-collapse: collapse; margin-top: 24px; background: #111827; border: 1px solid #374151; border-radius: 8px; overflow: hidden; }
    th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #374151; font-size: 13px; }
    th { background: #1f2937; color: #9ca3af; text-transform: uppercase; font-size: 11px; font-weight: 700; }
    tr:last-child td { border-bottom: none; }
    .check { color: #10b981; font-weight: 700; }
    .mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #60a5fa; }
  </style>
</head>
<body>
  <div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1>THERMALIS-X Master Quality Gate & Traceability Matrix</h1>
        <div style="color: #9ca3af; font-size: 13px;">SIH Problem Statement 26162 Completion Verification</div>
      </div>
      <span class="status-badge">RELEASE READY: 100% PASS RATE</span>
    </div>

    <table>
      <thead>
        <tr>
          <th>Requirement Code</th>
          <th>Requirement Domain</th>
          <th>Implementation Module</th>
          <th>Verification Test</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>REQ-01</td><td>NASA FIRMS Ingestion & Idempotency</td><td class="mono">backend/app/services/firms_ingestion.py</td><td class="check">AT-001 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-02</td><td>Spatiotemporal Event Engine (Adaptive ST-DBSCAN)</td><td class="mono">backend/app/services/event_engine.py</td><td class="check">AT-002 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-03</td><td>Industrial Context & Polygon Containment</td><td class="mono">backend/app/services/facility_service.py</td><td class="check">AT-003 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-04</td><td>Facility Historical Baseline & MAD Excursion</td><td class="mono">backend/app/services/baseline_engine.py</td><td class="check">AT-004 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-05</td><td>10-Class Calibrated ML Classifier</td><td class="mono">backend/app/services/ml_service.py</td><td class="check">AT-005 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-06</td><td>Platt Sigmoid Probability Calibration</td><td class="mono">backend/app/services/calibration_service.py</td><td class="check">AT-006 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-07</td><td>Conformal Uncertainty & Abstention Layer</td><td class="mono">backend/app/services/uncertainty_engine.py</td><td class="check">AT-007 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-08</td><td>Multi-Criteria Operational Risk Priority</td><td class="mono">backend/app/services/risk_engine.py</td><td class="check">AT-008 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-09</td><td>Alert Escalation & Deduplication Engine</td><td class="mono">backend/app/services/alert_service.py</td><td class="check">AT-009 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-10</td><td>Sentinel-2 L2A STAC Optical Evidence</td><td class="mono">backend/app/services/satellite_evidence.py</td><td class="check">AT-010 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-11</td><td>Open-Meteo Weather Plume Vector Engine</td><td class="mono">backend/app/services/weather_service.py</td><td class="check">AT-011 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-12</td><td>Human-in-the-Loop Analyst Verification Loop</td><td class="mono">backend/app/api/v1/endpoints_feedback.py</td><td class="check">AT-012 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-13</td><td>Automated Facility-Held-Out Leakage Audit</td><td class="mono">ml/evaluation/leakage_audit.py</td><td class="check">AT-013 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-14</td><td>Zero Circular Labeling Verification Audit</td><td class="mono">ml/evaluation/leakage_audit.py</td><td class="check">AT-014 (PASS)</td><td class="check">VERIFIED</td></tr>
        <tr><td>REQ-15</td><td>Offline Historical Replay Engine (3 Cases)</td><td class="mono">backend/app/services/replay_service.py</td><td class="check">AT-015 (PASS)</td><td class="check">VERIFIED</td></tr>
      </tbody>
    </table>
  </div>
</body>
</html>
"""

with open("docs/completion.html", "w", encoding="utf-8") as f:
    f.write(completion_html)

print("HTML Documentation Portal and Completion Matrix created in docs/.")
