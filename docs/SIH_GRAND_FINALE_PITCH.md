# THERMALIS-X: SIH Grand Finale Pitch & Jury Defense Guide
**Problem Statement 26162**: AI-Based Detection and Classification of Industrial Fires and Persistent Thermal Sources Using NASA FIRMS, OSM & Satellite Data

---

## 1. The 3-Minute Grand Finale Elevator Pitch

> *"Respected Jury Members, every industrial refinery, steel mill, and petrochemical complex in India flares high-temperature gas and operates high-heat kilns 24 hours a day, 365 days a year.
> 
> When standard satellite fire algorithms or naive AI models process NASA FIRMS data, they see extreme thermal radiation and immediately trigger emergency alarms. This produces hundreds of false fire alarms every single week, overwhelming disaster response agencies and causing critical alert fatigue.
> 
> Worse, when an actual catastrophe occurs—such as the HPCL Vizag refinery tank blaze—the fire begins inside an already hot facility. Existing systems simply assume it's normal operational heat until the disaster has already spread off-site.
> 
> **THERMALIS-X solves this fundamental paradox through our core axiom: Industrial Proximity is NOT Industrial Fire.**
> 
> We have built the first end-to-end spatiotemporal thermal intelligence system that:
> 1. Dynamically maps facility boundaries using OpenStreetMap and Global Energy Monitor data.
> 2. Builds 180-day robust statistical thermal baselines using Median Absolute Deviation (MAD) for every facility in India.
> 3. Employs a 10-class calibrated XGBoost model paired with finite-sample **Split Conformal Prediction** to mathematically guarantee uncertainty bounds.
> 4. Generates instant NDMA / ERG 2024 Incident Command System (ICS-201) emergency evacuation corridors and multi-agency dispatch orders in sub-second response times.
> 
> THERMALIS-X transforms raw spaceborne infrared telemetry into actionable, life-saving industrial disaster command."*

---

## 2. The 5-Minute Live Demonstration Protocol

| Minute | Action / UI Click | Voiceover & Key Takeaway |
| :---: | :--- | :--- |
| **00:00 - 01:00** | Open GIS Console (`http://localhost:8000`). Switch view to Vizag Refinery (`CASE-01-VIZAG`). | *"Here we observe the HPCL Visakhapatnam Refinery. The background shows our 180-day baseline median of 18 MW. Notice the red spike at 14:15 UTC reaching 142 MW. Our MAD Z-score surges to +8.2, classifying this not as routine flaring, but as a critical IND_ACCIDENT."* |
| **01:00 - 02:00** | Click on the Vizag event polygon. Open the Analytical Drawer. | *"Notice the Conformal Prediction Set: `{IND_ACCIDENT}`. Because the prediction set contains only one class, our model has high statistical confidence. The NDMA Risk Priority Engine scores this at 87.8/100 (CRITICAL)."* |
| **02:00 - 03:00** | Scroll down in the drawer to the **NDMA / ERG 2024 Evacuation Protocol**. | *"Look at the evacuation corridor: The system automatically fetched Open-Meteo wind vectors (3.5 km/h at 105°), computed the downwind plume dispersion heading (285°), and designated an immediate 1,000-meter isolation perimeter with SDRF/NDRF dispatch callouts."* |
| **03:00 - 04:00** | Click on **Historical Replay** -> Switch to **Jharia Coalfields** (`CASE-02-JHARIA`). | *"Now we examine Jharia Coalfield, Jharkhand. Thermal radiation has persisted for over 180 consecutive days with an areal footprint of 48 hectares. The model correctly identifies this as COAL_SEAM_FIRE, with 0 false alarms triggered for the surrounding mining plants."* |
| **04:00 - 05:00** | Click **Historical Replay** -> Switch to **Morbi Ceramics** (`CASE-03-MORBI`). | *"Finally, Morbi, Gujarat—the tile capital of the world. 800+ gas kilns fire simultaneously. THERMALIS-X tracks all 800 kilns within their normal baseline bounds, logging operational continuity with zero false dispatch orders."* |

---

## 3. The 10-Minute Technical & Domain Q&A Defense Matrix

### Q1: "What happens during heavy monsoon cloud cover when optical/infrared satellites are blinded?"
**Defense**: *"NASA FIRMS VIIRS (375m) operates in the Mid-Wave Infrared (MWIR 3.74 μm) band, which penetrates thin fog and light cloud cover far better than optical light. However, during thick monsoonal cumulonimbus cover, satellite thermal sensors cannot detect ground radiance.
Instead of silently failing or emitting false negatives, THERMALIS-X implements a **Degraded State Protocol**: when STAC queries return 100% cloud opacity over an industrial zone, the system widens its Conformal Prediction Set to include `{UNKNOWN_SOURCE}`, triggers the `CLOUDY_OPTICAL_DEGRADED` state, and switches to Synthetic Aperture Radar (Sentinel-1 C-SAR backscatter change detection) and ground CEMS sensor validation."*

### Q2: "A VIIRS pixel is 375 meters. How do you differentiate a 5-meter flare stack from a 100-meter accidental fire within the same pixel?"
**Defense**: *"We utilize the classic **Dozier (1981) Dual-Channel Radiative Transfer Model**. A high-temperature 5-meter flare stack at 1,200 K emits disproportionately in the 3.74 μm MWIR band compared to the 11 μm LWIR band. By solving the simultaneous Planck radiation equations across both channels, we derive the sub-pixel fractional area ($p$) and effective fire temperature ($T_f$). A flare stack exhibits a tiny sub-pixel area ($p < 0.005$) and high temperature ($>1,000\text{ K}$), whereas an accidental fuel fire exhibits an expanding area ($p > 0.05$) at 600–900 K. We also fuse 20-meter Sentinel-2 SWIR bands (B11/B12) whenever a revisit is available."*

### Q3: "Why not use a modern Large Language Model (LLM) or a simple distance threshold?"
**Defense**: *"A distance threshold suffers from the **Circularity Trap**: if you define 'anything near a factory is a factory flare', you will miss all accidental factory fires. If you define 'anything near a factory is an accidental fire', you trigger hundreds of false alarms per day from routine flaring.
LLMs, on the other hand, are non-deterministic, have high inference latency (seconds vs milliseconds), hallucinate geographic coordinates, and lack spatial geometric reasoning. THERMALIS-X uses deterministic PostGIS topology, rolling MAD statistics, and calibrated XGBoost with Conformal Prediction sets—providing millisecond inference, zero hallucination, and rigorous mathematical guarantees."*

### Q4: "How does the system ensure disaster responders don't suffer from alert fatigue?"
**Defense**: *"We implement a 3-tier filtration architecture:
1. **Physical Excursion Filter**: An event is only considered abnormal if its FRP exceeds the facility's 180-day baseline by more than 3 Median Absolute Deviations ($Z_{\text{MAD}} > 3.0$).
2. **Probability Calibration**: Raw ML scores are Platt-calibrated to true empirical probabilities. If entropy is high ($>0.60$), the system abstains from triggering high-priority alarms.
3. **Stateful Alert Cooldown**: A facility cannot trigger repetitive alarms within a 60-minute window unless FRP surges by more than 50%."*

### Q5: "Can THERMALIS-X run entirely offline in an air-gapped National Disaster Management bunker?"
**Defense**: *"Yes. THERMALIS-X requires zero internet connectivity during offline operation. The entire application runs on an embedded SQLite / DuckDB backend with pre-seeded Indian industrial facility footprints, local ONNX/XGBoost inference, offline Leaflet GIS tiles, and cached weather/historical replay data. In online mode, it hooks into NASA FIRMS NRT and Open-Meteo with automatic graceful degradation upon connection loss."*
