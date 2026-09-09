# THERMALIS-X Data Provenance & Satellite Observation Lineage
**Smart India Hackathon Problem Statement 26162**
**AI-Based Detection and Classification of Industrial Fires and Persistent Thermal Sources**

---

## 1. Executive Summary & Data Integrity Axiom

THERMALIS-X adheres to strict geospatial data provenance standards. Every satellite observation, GIS facility boundary, weather vector, and machine learning record is tracked with cryptographic verification (SHA-256), sensor metadata, temporal acquisition timestamps, and zero-leakage partition boundaries.

The core scientific premise of THERMALIS-X is:
Industrial Facility Proximity != Industrial Fire Disaster

A naive model associating high thermal radiation within an industrial compound as an 'accident' produces near-100% false alarm rates because refineries, petrochemical plants, steel mills, and cement works operate legitimate, high-temperature thermal processes (e.g., continuous flaring, blast furnace tapping, calciner exhaust). THERMALIS-X decouples **Source Identity** (what the emitter is) from **Abnormality State** (whether the emitter is operating within its normal 180-day baseline envelope or experiencing an excursion).

---

## 2. Remote Sensing Satellite Data Sources

| Sensor / Satellite Constellation | Product Code | Spatial Resolution | Temporal Revisit | Primary Spectral Bands | Data Provider & License |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **VIIRS / Suomi-NPP** | VNP14IMGTDL | 375 m at nadir | ~12 hours (day/night) | I4 (3.9 um MWIR), I5 (11.5 um LWIR) | NASA FIRMS / Public Domain (NASA Open Data) |
| **VIIRS / NOAA-20 (JPSS-1)** | VJ114IMGTDL | 375 m at nadir | ~12 hours (offset ~50 min from S-NPP) | I4 (3.9 um), I5 (11.5 um) | NASA FIRMS / Public Domain |
| **VIIRS / NOAA-21 (JPSS-2)** | VJ214IMGTDL | 375 m at nadir | ~12 hours (offset constellation) | I4 (3.9 um), I5 (11.5 um) | NASA FIRMS / Public Domain |
| **MODIS / Terra & Aqua** | MOD14DL / MYD14DL | 1000 m (1 km) | 4 passes/day combined | Band 21/22 (3.9 um), Band 31 (11 um) | NASA FIRMS / Public Domain |
| **Sentinel-2 MSI (L2A)** | S2A/S2B MSI L2A | 10 m / 20 m | 5 days (with twin constellation) | B12 (2.19 um SWIR-2), B11 (1.61 um SWIR-1), B8A (865 nm NIR) | ESA Copernicus / Creative Commons CC-BY 4.0 |
| **Landsat 8/9 OLI/TIRS** | LC08/LC09 L2SP | 30 m (SWIR) / 100 m (TIR) | 8 days (paired 8/9) | Band 7 (2.2 um), Band 6 (1.57 um), Band 10 (10.9 um) | USGS / Landsat Data Policy |

### Ingestion Protocol & Validation
Every active fire detection ingested from FIRMS passes through backend/app/services/firms_ingestion.py:
1. Latitude/Longitude Boundary Check: WGS-84 coordinate validation (-90 <= lat <= 90, -180 <= lon <= 180).
2. Brightness Temperature Plausibility: 200.0 K <= T_b <= 500.0 K.
3. Fire Radiative Power (FRP): 0.0 MW <= FRP <= 10,000.0 MW.
4. Confidence Class: Categorical mapped from nominal, low, high or integer confidence [0, 100].
5. SHA-256 Idempotency: Deduplication hash calculated as SHA256(satellite + lat + lon + acq_date + acq_time). Guarantees zero duplicate entries across overlapping API passes.

---

## 3. Industrial Infrastructure & Geospatial Context

1. OpenStreetMap (OSM) Curated Industrial Footprints:
   - Polygons extracted using Overpass API with queries on man_made=works, landuse=industrial, industrial=*, power=plant, craft=*.
   - Polygons are validated as closed planar polygons with EPSG:4326 / WGS-84 coordinates.
   - Point-in-polygon containment uses Shapely Point(lon, lat) evaluated against shape(geom).contains(pt).
   - Distance to nearest boundary calculated via Haversine great-circle distance algorithm.
   - License: Open Database License (ODbL) 1.0.

2. Land Cover & Terrain Classification:
   - Primary: ESA WorldCover 10 m resolution global land cover product based on Sentinel-1 and Sentinel-2.
   - Classes mapped: Built-up/Industrial (50), Cropland (40), Tree Cover/Forest (10), Grassland/Shrubland (20/30), Bare/Sparse/Mining (60), Water Bodies (80).
   - License: Creative Commons Attribution 4.0 International (CC-BY 4.0).

3. Atmospheric & Meteorological Context:
   - Dynamic 10 m surface wind speed (u, v components in km/h), wind direction (0-360 deg), surface temperature (deg C), relative humidity (%), and boundary layer height (m).
   - Provider: Open-Meteo Global Historical Weather & ECMWF / GFS Numerical Weather Prediction Models.

---

## 4. Benchmark Datasets & Partitioning Scheme

- data/processed/benchmark_dataset_v1.parquet: Binary Apache Parquet columnar store, Snappy compression.
- data/processed/benchmark_dataset_v1.csv: RFC 4180 compliant CSV export for interoperability.
- Total benchmark records: 2,500 samples across 10 balanced operational classes.

### Spatial Facility-Held-Out Split Protocol (Strict Zero-Leakage)
- Facilities are strictly partitioned into:
  - Train Set (70%): FAC-REG-001 through FAC-REG-014.
  - Validation Set (15%): FAC-REG-015 through FAC-REG-017.
  - Test Set (15%): FAC-REG-018 through FAC-REG-020.
- Zero Spatial Overlap: No facility appearing in the test set has ever been seen during training.
- Distance Distribution: Average distance from facility centroid is equalized across classes to prevent the classifier from trivially predicting IND_ACCIDENT based solely on facility proximity.

---

## 5. Ground Truth Case Study Telemetry Files

The repository contains three complete, high-resolution historical telemetry files in data/cases/:
1. Case Study 1: HPCL Visakhapatnam Refinery Storage Tank Fire (data/cases/case_01_vizag_refinery/case_data.json)
2. Case Study 2: Jharia Coalfield Subsurface Spontaneous Combustion (data/cases/case_02_jharia_coalfield/case_data.json)
3. Case Study 3: Morbi Ceramics Industrial Cluster vs Agricultural Stubble Burning (data/cases/case_03_morbi_ceramics/case_data.json)

---

## 6. Cryptographic Manifest & Verification

All data assets are verified against data/manifests/data_manifest.json. Verification command:
python scripts/export_data_assets.py
