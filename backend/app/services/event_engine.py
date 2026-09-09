import json
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
