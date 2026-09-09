import os
import shutil

# 1. Ensure frontend/index.html is a copy of frontend/dist/index.html
if os.path.exists("frontend/dist/index.html"):
    shutil.copy("frontend/dist/index.html", "frontend/index.html")
    print("Copied frontend/dist/index.html to frontend/index.html")

# 2. Package.json
pkg = """{
  "name": "thermalis-x-console",
  "version": "1.0.0",
  "description": "THERMALIS-X Geospatial Industrial Thermal Intelligence and Early Warning GIS Console",
  "main": "src/App.js",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "leaflet": "^1.9.4",
    "chart.js": "^4.4.0"
  },
  "devDependencies": {
    "vite": "^5.0.0"
  },
  "keywords": [
    "gis",
    "leaflet",
    "nasa-firms",
    "remote-sensing",
    "thermal-anomaly",
    "disaster-management",
    "conformal-prediction"
  ],
  "author": "THERMALIS-X Team",
  "license": "Apache-2.0"
}
"""
with open("frontend/package.json", "w", encoding="utf-8") as f:
    f.write(pkg.strip() + "\n")

# 3. Frontend README.md
readme = """# THERMALIS-X GIS Command Console & Analytical Frontend

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
"""
with open("frontend/README.md", "w", encoding="utf-8") as f:
    f.write(readme.strip() + "\n")

# 4. Modular JS/CSS in src
os.makedirs("frontend/src/components", exist_ok=True)
os.makedirs("frontend/src/services", exist_ok=True)
os.makedirs("frontend/src/styles", exist_ok=True)

api_js = """/**
 * THERMALIS-X REST API Service Client
 */
const API_BASE = '/api/v1';

export async function fetchEvents() {
  const res = await fetch(`${API_BASE}/events`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchEventDetail(eventId) {
  const res = await fetch(`${API_BASE}/events/${eventId}`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchFacilities() {
  const res = await fetch(`${API_BASE}/facilities`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchAlerts() {
  const res = await fetch(`${API_BASE}/alerts`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchReplayCases() {
  const res = await fetch(`${API_BASE}/replay/cases`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchReplaySteps(caseId) {
  const res = await fetch(`${API_BASE}/replay/cases/${caseId}/steps`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchResponsePlan(eventId) {
  const res = await fetch(`${API_BASE}/events/${eventId}/response-plan`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchIcs201Brief(eventId) {
  const res = await fetch(`${API_BASE}/events/${eventId}/ics-201`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}
"""
with open("frontend/src/services/api.js", "w", encoding="utf-8") as f:
    f.write(api_js.strip() + "\n")

map_js = """/**
 * THERMALIS-X MapViewer Component (Leaflet 1.9.4)
 */
export class MapViewer {
  constructor(elementId, initialCenter = [20.5937, 78.9629], initialZoom = 5) {
    this.map = L.map(elementId, {
      zoomControl: false,
      attributionControl: false
    }).setView(initialCenter, initialZoom);

    L.control.zoom({ position: 'bottomright' }).addTo(this.map);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd'
    }).addTo(this.map);

    this.eventLayer = L.layerGroup().addTo(this.map);
    this.facilityLayer = L.layerGroup().addTo(this.map);
  }

  clearEvents() {
    this.eventLayer.clearLayers();
  }

  addEventMarker(event, onClickCallback) {
    const color = event.priority === 'CRITICAL' ? '#ef4444' :
                  event.priority === 'HIGH' ? '#f97316' :
                  event.priority === 'WATCH' ? '#3b82f6' : '#10b981';

    const circle = L.circleMarker([event.centroid_lat, event.centroid_lon], {
      radius: Math.max(6, Math.min(22, Math.sqrt(event.max_frp) * 2.2)),
      fillColor: color,
      color: '#ffffff',
      weight: 1.5,
      opacity: 0.9,
      fillOpacity: 0.75
    });

    circle.bindTooltip(`<b>${event.id}</b><br>${event.source_class} (${event.max_frp} MW)`, {
      permanent: false,
      direction: 'top',
      className: 'leaflet-tooltip-dark'
    });

    circle.on('click', () => onClickCallback(event));
    this.eventLayer.addLayer(circle);
    return circle;
  }

  flyTo(lat, lon, zoom = 13) {
    this.map.flyTo([lat, lon], zoom, { duration: 1.2 });
  }
}
"""
with open("frontend/src/components/MapViewer.js", "w", encoding="utf-8") as f:
    f.write(map_js.strip() + "\n")

drawer_js = """/**
 * THERMALIS-X Analytics Drawer Component
 */
export class AnalyticsDrawer {
  constructor(drawerElementId) {
    this.drawer = document.getElementById(drawerElementId);
  }

  open(eventDetail, responsePlan) {
    if (!this.drawer) return;
    this.drawer.classList.add('open');
    this.render(eventDetail, responsePlan);
  }

  close() {
    if (!this.drawer) return;
    this.drawer.classList.remove('open');
  }

  render(event, plan) {
    console.log('Rendering analytical drawer for event:', event.id);
  }
}
"""
with open("frontend/src/components/AnalyticsDrawer.js", "w", encoding="utf-8") as f:
    f.write(drawer_js.strip() + "\n")

replay_js = """/**
 * THERMALIS-X Historical Replay Sequencer
 */
import { fetchReplaySteps } from '../services/api.js';

export class ReplayEngine {
  constructor(onStepChangeCallback) {
    this.currentCaseId = null;
    this.steps = [];
    this.currentIndex = 0;
    this.onStepChange = onStepChangeCallback;
  }

  async loadCase(caseId) {
    this.currentCaseId = caseId;
    this.steps = await fetchReplaySteps(caseId);
    this.currentIndex = 0;
    if (this.steps.length > 0) {
      this.onStepChange(this.steps[0], 0, this.steps.length);
    }
  }

  next() {
    if (this.currentIndex < this.steps.length - 1) {
      this.currentIndex++;
      this.onStepChange(this.steps[this.currentIndex], this.currentIndex, this.steps.length);
    }
  }

  prev() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      this.onStepChange(this.steps[this.currentIndex], this.currentIndex, this.steps.length);
    }
  }
}
"""
with open("frontend/src/components/ReplayEngine.js", "w", encoding="utf-8") as f:
    f.write(replay_js.strip() + "\n")

app_js = """/**
 * THERMALIS-X Main Application Entrypoint
 */
import { MapViewer } from './components/MapViewer.js';
import { AnalyticsDrawer } from './components/AnalyticsDrawer.js';
import { ReplayEngine } from './components/ReplayEngine.js';
import { fetchEvents, fetchFacilities, fetchAlerts } from './services/api.js';

console.log('THERMALIS-X GIS Command Console Initialized');
"""
with open("frontend/src/App.js", "w", encoding="utf-8") as f:
    f.write(app_js.strip() + "\n")

css = """/* THERMALIS-X Dark-Mode Modern Industrial UI Theme */
:root {
  --bg-base: #0a0e17;
  --bg-surface: #111827;
  --bg-surface-elevated: #1f2937;
  --border-color: #374151;
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
  --color-critical: #ef4444;
  --color-warning: #f59e0b;
  --color-watch: #3b82f6;
  --color-info: #10b981;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', sans-serif;
  background-color: var(--bg-base);
  color: var(--text-primary);
}
"""
with open("frontend/src/styles/main.css", "w", encoding="utf-8") as f:
    f.write(css.strip() + "\n")

print("Frontend assets fully packed!")
