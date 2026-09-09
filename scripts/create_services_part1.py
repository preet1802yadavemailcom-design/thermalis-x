import os

firms_ingestion = """import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
import httpx
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.error_codes import ErrorCode

class FIRMSValidator:
    @staticmethod
    def validate_record(record: Dict[str, Any]) -> Tuple[str, List[str]]:
        reasons = []
        lat = record.get("latitude")
        lon = record.get("longitude")
        frp = record.get("frp", 0.0)
        brightness = record.get("brightness", 300.0)

        if lat is None or lon is None:
            return "INVALID", ["missing_coordinates"]
        try:
            lat = float(lat)
            lon = float(lon)
            if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
                return "INVALID", ["coordinates_out_of_bounds"]
        except (ValueError, TypeError):
            return "INVALID", ["malformed_coordinates"]

        try:
            frp = float(frp)
            if frp < 0.0 or frp > 15000.0:
                reasons.append("impossible_frp")
        except (ValueError, TypeError):
            reasons.append("malformed_frp")

        try:
            brightness = float(brightness)
            if brightness < 200.0 or brightness > 600.0:
                reasons.append("suspect_brightness_temperature")
        except (ValueError, TypeError):
            reasons.append("malformed_brightness")

        if "acq_date" not in record and "acq_datetime" not in record:
            return "INVALID", ["missing_timestamp"]

        if reasons:
            return "SUSPECT", reasons
        return "VALID", []

    @staticmethod
    def compute_raw_hash(record: Dict[str, Any]) -> str:
        unique_str = f"{record.get('satellite')}_{record.get('latitude')}_{record.get('longitude')}_{record.get('acq_date')}_{record.get('acq_time')}_{record.get('frp')}"
        return hashlib.sha256(unique_str.encode("utf-8")).hexdigest()

class FIRMSConnector:
    def __init__(self):
        self.base_url = settings.FIRMS_BASE_URL
        self.map_key = settings.FIRMS_MAP_KEY

    async def fetch_nrt(self, source: str = "VIIRS_NOAA20_NRT", country: str = "IND", days: int = 1) -> List[Dict[str, Any]]:
        if settings.DEMO_MODE or self.map_key == "SAMPLE_FIRMS_MAP_KEY":
            logger.info("DEMO_MODE enabled or default key present. FIRMS live fetch operating in resilient fallback mode.")
            return []
        
        url = f"{self.base_url}/country/csv/{self.map_key}/{source}/{country}/{days}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    lines = resp.text.strip().split("\n")
                    if len(lines) > 1:
                        headers = lines[0].split(",")
                        records = []
                        for line in lines[1:]:
                            vals = line.split(",")
                            if len(vals) == len(headers):
                                rec = dict(zip(headers, vals))
                                records.append(rec)
                        return records
                logger.warning(f"FIRMS API returned status {resp.status_code}: {resp.text[:200]}")
                return []
        except Exception as e:
            logger.error(f"FIRMS API request error: {str(e)}", extra={"error_code": ErrorCode.FIRMS_SENSOR_UNAVAILABLE})
            return []
"""

with open("backend/app/services/firms_ingestion.py", "w", encoding="utf-8") as f:
    f.write(firms_ingestion)

facility_service = """import math
import json
from typing import List, Dict, Any, Optional, Tuple

class FacilityService:
    # Curated Indian Industrial Facilities for Mission-Critical Context
    CURATED_FACILITIES: List[Dict[str, Any]] = [
        {
            "id": "FAC-VIZAG-001",
            "name": "HPCL Visakhapatnam Refinery",
            "facility_type": "refinery",
            "latitude": 17.7012,
            "longitude": 83.2568,
            "source": "VERIFIED_INDUSTRIAL",
            "source_confidence": 0.99,
            "baseline_median_frp": 18.5,
            "baseline_mad_frp": 4.2,
            "baseline_p90_frp": 27.0,
            "baseline_p99_frp": 38.0,
            "baseline_obs_count": 420,
            "footprint_geojson": json.dumps({
                "type": "Polygon",
                "coordinates": [[[83.245, 17.690], [83.270, 17.690], [83.270, 17.715], [83.245, 17.715], [83.245, 17.690]]]
            })
        },
        {
            "id": "FAC-JHARIA-002",
            "name": "BCCL Jharia Coal Mines Complex",
            "facility_type": "coal_mine",
            "latitude": 23.7510,
            "longitude": 86.4150,
            "source": "GEM_COAL",
            "source_confidence": 0.95,
            "baseline_median_frp": 12.0,
            "baseline_mad_frp": 3.1,
            "baseline_p90_frp": 19.5,
            "baseline_p99_frp": 28.0,
            "baseline_obs_count": 890,
            "footprint_geojson": json.dumps({
                "type": "Polygon",
                "coordinates": [[[86.390, 23.730], [86.440, 23.730], [86.440, 23.775], [86.390, 23.775], [86.390, 23.730]]]
            })
        },
        {
            "id": "FAC-MORBI-003",
            "name": "Morbi Ceramic Industrial Zone",
            "facility_type": "ceramic_manufacturing",
            "latitude": 22.8210,
            "longitude": 70.8350,
            "source": "OSM_INDUSTRIAL",
            "source_confidence": 0.92,
            "baseline_median_frp": 8.0,
            "baseline_mad_frp": 2.0,
            "baseline_p90_frp": 13.0,
            "baseline_p99_frp": 18.0,
            "baseline_obs_count": 310,
            "footprint_geojson": json.dumps({
                "type": "Polygon",
                "coordinates": [[[70.810, 22.800], [70.860, 22.800], [70.860, 22.845], [70.810, 22.845], [70.810, 22.800]]]
            })
        },
        {
            "id": "FAC-PARADEEP-004",
            "name": "IOCL Paradeep Petrochemical Complex",
            "facility_type": "petrochemical",
            "latitude": 20.2850,
            "longitude": 86.6650,
            "source": "VERIFIED_INDUSTRIAL",
            "source_confidence": 0.98,
            "baseline_median_frp": 24.0,
            "baseline_mad_frp": 5.5,
            "baseline_p90_frp": 35.0,
            "baseline_p99_frp": 48.0,
            "baseline_obs_count": 512,
            "footprint_geojson": json.dumps({
                "type": "Polygon",
                "coordinates": [[[86.640, 20.260], [86.690, 20.260], [86.690, 20.310], [86.640, 20.310], [86.640, 20.260]]]
            })
        },
        {
            "id": "FAC-TATASTEEL-005",
            "name": "Tata Steel Works Jamshedpur",
            "facility_type": "steel",
            "latitude": 22.7950,
            "longitude": 86.2050,
            "source": "GEM_STEEL",
            "source_confidence": 0.97,
            "baseline_median_frp": 32.0,
            "baseline_mad_frp": 6.8,
            "baseline_p90_frp": 46.0,
            "baseline_p99_frp": 62.0,
            "baseline_obs_count": 640,
            "footprint_geojson": json.dumps({
                "type": "Polygon",
                "coordinates": [[[86.180, 22.775], [86.230, 22.775], [86.230, 22.815], [86.180, 22.815], [86.180, 22.775]]]
            })
        }
    ]

    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    def find_nearest_facility(self, lat: float, lon: float, max_dist_km: float = 10.0) -> Tuple[Optional[Dict[str, Any]], float]:
        nearest_fac = None
        min_dist = float("inf")

        for fac in self.CURATED_FACILITIES:
            dist = self.haversine_km(lat, lon, fac["latitude"], fac["longitude"])
            if dist < min_dist:
                min_dist = dist
                nearest_fac = fac

        if nearest_fac and min_dist <= max_dist_km:
            return nearest_fac, round(min_dist, 3)
        return None, round(min_dist, 3) if nearest_fac else 999.0

    def is_inside_facility(self, lat: float, lon: float, facility: Dict[str, Any]) -> bool:
        if not facility.get("footprint_geojson"):
            return False
        try:
            geom = json.loads(facility["footprint_geojson"])
            coords = geom["coordinates"][0]
            # Ray casting point in polygon algorithm
            n = len(coords)
            inside = False
            p1x, p1y = coords[0]
            for i in range(n + 1):
                p2x, p2y = coords[i % n]
                if lon > min(p1x, p2x):
                    if lon <= max(p1x, p2x):
                        if lat <= max(p1y, p2y):
                            if p1y != p2y:
                                xints = (lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or lon <= xints:
                                inside = not inside
                p1x, p1y = p2x, p2y
            return inside
        except Exception:
            return False
"""

with open("backend/app/services/facility_service.py", "w", encoding="utf-8") as f:
    f.write(facility_service)

baseline_engine = """import numpy as np
from typing import List, Dict, Any

class FacilityBaselineEngine:
    @staticmethod
    def compute_baseline_profile(historical_frp: List[float]) -> Dict[str, float]:
        if not historical_frp:
            return {
                "median_frp": 0.0,
                "mad_frp": 0.0,
                "p10_frp": 0.0,
                "p90_frp": 0.0,
                "p99_frp": 0.0,
                "count": 0
            }
        arr = np.array(historical_frp, dtype=float)
        median = float(np.median(arr))
        # Median Absolute Deviation (MAD)
        mad = float(np.median(np.abs(arr - median)))
        p10 = float(np.percentile(arr, 10))
        p90 = float(np.percentile(arr, 90))
        p99 = float(np.percentile(arr, 99))
        return {
            "median_frp": round(median, 2),
            "mad_frp": round(mad, 2),
            "p10_frp": round(p10, 2),
            "p90_frp": round(p90, 2),
            "p99_frp": round(p99, 2),
            "count": len(arr)
        }

    @staticmethod
    def calculate_excursion(current_frp: float, baseline: Dict[str, Any]) -> Dict[str, Any]:
        median = baseline.get("baseline_median_frp", 0.0)
        mad = baseline.get("baseline_mad_frp", 0.0)
        p90 = baseline.get("baseline_p90_frp", 0.0)
        p99 = baseline.get("baseline_p99_frp", 0.0)

        # Scale factor 1.4826 makes MAD an unbiased estimator of standard deviation for normal dist
        sigma_robust = 1.4826 * mad if mad > 0.01 else 2.0
        z_score = (current_frp - median) / sigma_robust

        is_excursion = (current_frp > p99) or (z_score > 3.0)
        ratio = current_frp / max(1.0, median)

        return {
            "frp_zscore": round(float(z_score), 2),
            "frp_to_baseline_ratio": round(float(ratio), 2),
            "is_baseline_excursion": bool(is_excursion),
            "exceeds_p90": bool(current_frp > p90),
            "exceeds_p99": bool(current_frp > p99)
        }
"""

with open("backend/app/services/baseline_engine.py", "w", encoding="utf-8") as f:
    f.write(baseline_engine)

event_engine = """import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np
from shapely.geometry import MultiPoint, Point
from backend.app.services.facility_service import FacilityService
from backend.app.config import settings

class EventEngine:
    def __init__(self):
        self.spatial_eps_km = settings.SPATIAL_CLUSTER_RADIUS_KM
        self.temporal_eps_hours = settings.TEMPORAL_WINDOW_HOURS
        self.facility_service = FacilityService()

    def cluster_observations(self, observations: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        if not observations:
            return []

        # Sort chronologically
        sorted_obs = sorted(observations, key=lambda x: x["acq_datetime"])
        clusters: List[List[Dict[str, Any]]] = []

        for obs in sorted_obs:
            assigned = False
            lat = obs["latitude"]
            lon = obs["longitude"]
            t_curr = obs["acq_datetime"]

            for cluster in clusters:
                # Test against cluster members
                matches = False
                for member in cluster:
                    dt = abs((t_curr - member["acq_datetime"]).total_seconds()) / 3600.0
                    if dt <= self.temporal_eps_hours:
                        dist = self.facility_service.haversine_km(lat, lon, member["latitude"], member["longitude"])
                        if dist <= self.spatial_eps_km:
                            matches = True
                            break
                if matches:
                    cluster.append(obs)
                    assigned = True
                    break

            if not assigned:
                clusters.append([obs])

        return clusters

    def construct_event_record(self, event_id: str, cluster: List[Dict[str, Any]], parent_event_id: Optional[str] = None) -> Dict[str, Any]:
        lats = [o["latitude"] for o in cluster]
        lons = [o["longitude"] for o in cluster]
        frps = [o["frp"] for o in cluster]
        times = [o["acq_datetime"] for o in cluster]

        centroid_lat = float(np.mean(lats))
        centroid_lon = float(np.mean(lons))
        first_seen = min(times)
        last_seen = max(times)
        duration_hours = max(0.0, (last_seen - first_seen).total_seconds() / 3600.0)

        # Spatial geometry & convex hull via Shapely
        if len(cluster) >= 3:
            pts = MultiPoint([(lon, lat) for lat, lon in zip(lats, lons)])
            hull = pts.convex_hull
            hull_geojson = json.dumps(hull.__geo_interface__)
            # Approx area in hectares using planar projection for small local bounds
            # 1 deg lat ~ 111 km, 1 deg lon ~ 111 km * cos(lat)
            lat_scale = 111.0
            lon_scale = 111.0 * math.cos(math.radians(centroid_lat))
            area_sq_km = hull.area * lat_scale * lon_scale
            area_ha = round(area_sq_km * 100.0, 2)
        elif len(cluster) == 2:
            hull_geojson = json.dumps({
                "type": "LineString",
                "coordinates": [[lons[0], lats[0]], [lons[1], lats[1]]]
            })
            area_ha = 1.0
        else:
            hull_geojson = json.dumps({
                "type": "Point",
                "coordinates": [centroid_lon, centroid_lat]
            })
            area_ha = 0.5

        # FRP Trend (slope)
        if len(cluster) > 1 and duration_hours > 0:
            time_offsets = [(t - first_seen).total_seconds() / 3600.0 for t in times]
            if np.std(time_offsets) > 1e-3:
                slope, _ = np.polyfit(time_offsets, frps, 1)
                frp_trend = round(float(slope), 2)
            else:
                frp_trend = 0.0
        else:
            frp_trend = 0.0

        # Total FRE (Fire Radiative Energy) MJ
        # Trapezoidal or duration * mean_frp * 3600 / 1e6 * 1000
        mean_frp = float(np.mean(frps))
        max_frp = float(np.max(frps))
        total_fre_mj = round(mean_frp * max(1.0, duration_hours) * 3600.0 * 1e-3, 1)

        # Nearest facility context
        fac, dist_km = self.facility_service.find_nearest_facility(centroid_lat, centroid_lon)

        return {
            "id": event_id,
            "status": "ACTIVE",
            "first_seen": first_seen,
            "last_seen": last_seen,
            "duration_hours": round(duration_hours, 2),
            "observation_count": len(cluster),
            "centroid_lat": round(centroid_lat, 5),
            "centroid_lon": round(centroid_lon, 5),
            "convex_hull_geojson": hull_geojson,
            "area_ha": max(0.1, area_ha),
            "max_frp": round(max_frp, 2),
            "mean_frp": round(mean_frp, 2),
            "total_fre_mj": total_fre_mj,
            "frp_trend": frp_trend,
            "nearest_facility_id": fac["id"] if fac else None,
            "distance_to_facility_km": dist_km,
            "parent_event_id": parent_event_id,
            "lineage_type": "INITIAL" if not parent_event_id else "CONTINUATION"
        }
"""

with open("backend/app/services/event_engine.py", "w", encoding="utf-8") as f:
    f.write(event_engine)

print("FIRMS Ingestion, Facility Service, Baseline Engine, and Event Engine written.")
