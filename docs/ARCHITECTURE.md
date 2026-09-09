# THERMALIS-X System Architecture & Technical Specifications

## 1. High-Level Dataflow Topology
THERMALIS-X is engineered as an asynchronous, event-driven geospatial intelligence pipeline:
```
[ NASA FIRMS (VIIRS/MODIS) ]
          │ (REST API / NRT Ingest / Replay)
          ▼
[ Ingestion & Quality Quarantine ] ─── (Status: VALID, SUSPECT, INVALID)
          │
          ▼
[ Spatiotemporal Event Engine (Adaptive ST-DBSCAN) ]
          │ (eps_spatial=1.25km, eps_temporal=24h, Convex Hull, Area, FRP Trend)
          ▼
[ Industrial Infrastructure Spatial Index (OSM / GEM) ]
          │ (Point-in-Polygon, Nearest-Neighbor Distance, Hazardous Tagging)
          ▼
[ Facility Baseline Engine (Robust Rolling Median & MAD) ]
          │ (FRP Excursion Z-Score, Envelope Check)
          ▼
[ Feature Pipeline (48 Dimensional Feature Matrix) ]
          │
          ▼
[ Calibrated Gradient Booster (XGBoost / LightGBM) ]
          │ (Platt Scaling, Shannon Entropy, Top Margin Abstention)
          ▼
[ Multi-Criteria Operational Priority & Alert Engine ]
          │ (INFORMATIONAL, WATCH, WARNING, CRITICAL with State Machine)
          ▼
[ Interactive GIS Operations Console & Analyst Feedback ]
```

## 2. Component Design & Responsibilities
- **Backend Framework**: FastAPI asynchronous ASGI framework.
- **Relational Persistence**: PostgreSQL with PostGIS extensions (with seamless zero-dependency SQLite fallback).
- **Geospatial Processing**: Shapely 2.0+ planar geometry operations and Haversine geodesic distance algorithms.
- **Machine Learning Engine**: XGBoost 3.3.0 and LightGBM with 5-fold facility-held-out cross-validation.
- **Explainability**: Grounded feature contribution attribution engine mapping directly to verifiable physical telemetry.
- **Frontend Console**: Zero-dependency Leaflet 1.9.4 GIS viewport with Chart.js analytics and high-contrast operational dark theme.
