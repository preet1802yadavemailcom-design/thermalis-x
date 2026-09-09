# THERMALIS-X GIS Command Console & Analytical Frontend

**Smart India Hackathon Problem Statement 26162**
*AI-Based Detection and Classification of Industrial Fires and Persistent Thermal Sources Using NASA FIRMS, OSM & Satellite Data*

---

## 1. Overview
The **THERMALIS-X Console** is a high-performance, dark-mode geospatial situational awareness dashboard designed for District Disaster Management Authorities (DDMA), industrial safety inspectors, and state emergency operation centers.

It is served directly by the FastAPI backend at `http://localhost:8000/` or can be built independently via Vite.

---

## 2. Key Architecture Components

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Geospatial Viewport** | Leaflet 1.9.4 + CartoDB Dark Matter | Interactive pan/zoom mapping of thermal anomalies, facility bounding polygons, and multi-sensor overlays. |
| **Thermal Radiative Charts** | Chart.js 4.x | Real-time temporal FRP progression plotted against 180-day facility baseline medians and MAD envelopes. |
| **Analytical Drawer** | Reactive Vanilla DOM / Modern ES6 | Deep-dive telemetry inspector displaying 10-class ML inference, Split Conformal Prediction sets C(X), and SHAP feature attribution waterfalls. |
| **NDMA / ERG 2024 Corridor** | Dynamic Spatial Engine | Real-time calculation of chemical disaster isolation distances, downwind plume corridors, and multi-agency dispatch callouts. |
| **Historical Replay System** | Stateful Step Sequencer | Step-by-step forensic progression across the 3 Indian benchmark disasters (HPCL Vizag, Jharia Coalfields, Morbi Ceramics). |
| **Data Feed Mode Toggle** | State Controller | Live NRT Satellite Feed vs Offline Historical Replay. |

---

## 3. Directory Layout
```
frontend/
|-- dist/
|   `-- index.html          # Production bundled, zero-dependency GIS console
|-- src/
|   |-- components/
|   |   |-- MapViewer.js    # Leaflet initialization, layer management, and polygon rendering
|   |   |-- AnalyticsDrawer.js # Telemetry inspection, conformal sets, and ERG evacuation card
|   |   `-- ReplayEngine.js # Historical case study step sequencer
|   |-- services/
|   |   `-- api.js          # REST client communicating with /api/v1/ endpoints
|   |-- styles/
|   |   `-- main.css        # Dark-mode industrial glassmorphism design system
|   `-- App.js              # Application entrypoint and event orchestration
|-- index.html              # Root developer entrypoint
|-- package.json            # Node/Vite dependency configuration
`-- README.md               # Frontend architecture and usage documentation
```

---

## 4. Running the Frontend

### Option A: Turnkey Execution (Recommended)
Run the root launcher:
- **Windows**: Double-click `run.bat` or execute `powershell scripts/run_demo.ps1`
- **Linux/macOS**: Execute `./run.sh`

The FastAPI server automatically serves the console at `http://localhost:8000/`.

### Option B: Standalone Node/Vite Development
```bash
cd frontend
npm install
npm run dev
```
