import json
import math
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Set, Tuple
import numpy as np
from shapely.geometry import MultiPoint, Point, Polygon
from backend.app.services.facility_service import FacilityService
from backend.app.config import settings

class EventEngine:
    """
    Spatiotemporal Density-Based Spatial Clustering of Applications with Noise (ST-DBSCAN).
    Based on Birant & Kut (2007): "ST-DBSCAN: An algorithm for clustering spatial-temporal datasets".
    
    Eliminates chain-linking artifacts inherent in single-linkage greedy clustering
    by requiring that cluster expansion propagates strictly through core points
    possessing at least MinPts spatiotemporal neighbors.
    """
    def __init__(
        self,
        spatial_eps_km: Optional[float] = None,
        temporal_eps_hours: Optional[float] = None,
        min_pts: int = 2
    ):
        self.spatial_eps_km = spatial_eps_km if spatial_eps_km is not None else settings.SPATIAL_CLUSTER_RADIUS_KM
        self.temporal_eps_hours = temporal_eps_hours if temporal_eps_hours is not None else settings.TEMPORAL_WINDOW_HOURS
        self.min_pts = max(1, min_pts)
        self.facility_service = FacilityService()

    def get_neighbors(self, idx: int, observations: List[Dict[str, Any]]) -> List[int]:
        """
        Finds all observations within spatial radius eps_s and temporal window eps_t of observation idx.
        Uses geodesic Haversine distance.
        """
        p = observations[idx]
        p_lat, p_lon = p["latitude"], p["longitude"]
        p_time = p["acq_datetime"]
        neighbors = []

        for j, q in enumerate(observations):
            # Temporal distance check
            dt_hours = abs((p_time - q["acq_datetime"]).total_seconds()) / 3600.0
            if dt_hours <= self.temporal_eps_hours:
                # Spatial geodesic distance check
                dist_km = self.facility_service.haversine_km(p_lat, p_lon, q["latitude"], q["longitude"])
                if dist_km <= self.spatial_eps_km:
                    neighbors.append(j)

        return neighbors

    def cluster_observations(self, observations: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Executes formal ST-DBSCAN clustering on input observations.
        Returns list of observation clusters. Noise points are returned as singleton events
        if MinPts <= 2, ensuring critical high-FRP single-observation thermal events are not discarded.
        """
        if not observations:
            return []

        n = len(observations)
        # Sorted chronologically for deterministic execution
        obs_sorted = sorted(observations, key=lambda x: x["acq_datetime"])

        visited = [False] * n
        cluster_assignments = [-1] * n  # -1 indicates unassigned or noise
        current_cluster_id = 0
        clusters_dict: Dict[int, List[Dict[str, Any]]] = {}

        for i in range(n):
            if visited[i]:
                continue
            visited[i] = True

            neighbors = self.get_neighbors(i, obs_sorted)

            if len(neighbors) < self.min_pts:
                # Mark as noise candidate (may later become border point)
                cluster_assignments[i] = -1
            else:
                # Point i is a CORE point: initiate new cluster expansion
                cluster_assignments[i] = current_cluster_id
                clusters_dict[current_cluster_id] = [obs_sorted[i]]

                queue = list(neighbors)
                # Expand cluster through density reachability
                while queue:
                    neighbor_idx = queue.pop(0)

                    if not visited[neighbor_idx]:
                        visited[neighbor_idx] = True
                        sub_neighbors = self.get_neighbors(neighbor_idx, obs_sorted)
                        if len(sub_neighbors) >= self.min_pts:
                            # Core point in neighborhood: append its neighbors to propagation queue
                            for sn in sub_neighbors:
                                if sn not in queue:
                                    queue.append(sn)

                    if cluster_assignments[neighbor_idx] == -1:
                        cluster_assignments[neighbor_idx] = current_cluster_id
                        clusters_dict[current_cluster_id].append(obs_sorted[neighbor_idx])

                current_cluster_id += 1

        # Collect formal clusters
        results = [clusters_dict[cid] for cid in sorted(clusters_dict.keys())]

        # For singleton unassigned / noise points: return them as isolated singleton clusters
        # so single-pass high-intensity flares or fires are preserved for operator inspection
        for i in range(n):
            if cluster_assignments[i] == -1:
                results.append([obs_sorted[i]])

        return results

    def construct_event_record(
        self,
        event_id: str,
        cluster: List[Dict[str, Any]],
        parent_event_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Constructs a complete event record with convex hull geometry, area in hectares,
        compactness ratio, and explicit onset/peak/end timestamps.
        """
        lats = [o["latitude"] for o in cluster]
        lons = [o["longitude"] for o in cluster]
        frps = [o["frp"] for o in cluster]
        times = [o["acq_datetime"] for o in cluster]

        centroid_lat = float(np.mean(lats))
        centroid_lon = float(np.mean(lons))

        # Explicit Timestamps
        onset_timestamp = min(times)
        end_timestamp = max(times)
        duration_hours = max(0.0, (end_timestamp - onset_timestamp).total_seconds() / 3600.0)

        # Peak FRP timestamp
        peak_idx = int(np.argmax(frps))
        peak_timestamp = times[peak_idx]
        report_timestamp = datetime.now(timezone.utc)

        # Spatial geometry & convex hull via Shapely
        if len(cluster) >= 3:
            pts = MultiPoint([(lon, lat) for lat, lon in zip(lats, lons)])
            hull = pts.convex_hull
            hull_geojson = json.dumps(hull.__geo_interface__)

            # Geodesic scaling for area and perimeter
            # 1 deg latitude ~ 111,000 meters; 1 deg longitude ~ 111,000 * cos(lat) meters
            lat_m = 111000.0
            lon_m = 111000.0 * math.cos(math.radians(centroid_lat))
            
            # Approximate area in m^2
            area_sqm = max(100.0, hull.area * lat_m * lon_m)
            area_ha = round(area_sqm / 10000.0, 2)
            
            # Perimeter approximation
            perimeter_m = max(10.0, hull.length * math.sqrt((lat_m**2 + lon_m**2) / 2.0))
            # Isoperimetric compactness ratio: 4 * pi * A / P^2
            compactness = round(min(1.0, (4.0 * math.pi * area_sqm) / (perimeter_m ** 2)), 4)
        elif len(cluster) == 2:
            hull_geojson = json.dumps({
                "type": "LineString",
                "coordinates": [[lons[0], lats[0]], [lons[1], lats[1]]]
            })
            area_ha = 1.0
            compactness = 0.50
        else:
            hull_geojson = json.dumps({
                "type": "Point",
                "coordinates": [lons[0], lats[0]]
            })
            area_ha = 0.5
            compactness = 1.00

        # FRP Trend (slope MW/hour)
        if len(cluster) >= 2 and duration_hours > 0.05:
            delta_t_hrs = [(t - onset_timestamp).total_seconds() / 3600.0 for t in times]
            # Simple linear regression slope
            cov = np.cov(delta_t_hrs, frps)
            var_t = np.var(delta_t_hrs)
            frp_trend = round(float(cov[0, 1] / var_t), 2) if var_t > 0 else 0.0
        else:
            frp_trend = 0.0

        # Total Fire Radiative Energy (FRE) approximation: FRE (MJ) = Integral FRP dt * 3600 / 1e6
        mean_frp = float(np.mean(frps))
        max_frp = float(np.max(frps))
        total_fre_mj = round(mean_frp * max(0.5, duration_hours) * 3600.0 / 1e6, 2)

        return {
            "id": event_id,
            "status": "ACTIVE",
            "first_seen": onset_timestamp,
            "last_seen": end_timestamp,
            "onset_timestamp": onset_timestamp.isoformat(),
            "peak_timestamp": peak_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
            "report_timestamp": report_timestamp.isoformat(),
            "duration_hours": round(duration_hours, 2),
            "observation_count": len(cluster),
            "centroid_lat": round(centroid_lat, 5),
            "centroid_lon": round(centroid_lon, 5),
            "convex_hull_geojson": hull_geojson,
            "area_ha": area_ha,
            "compactness": compactness,
            "max_frp": round(max_frp, 2),
            "mean_frp": round(mean_frp, 2),
            "total_fre_mj": total_fre_mj,
            "frp_trend": frp_trend,
            "parent_event_id": parent_event_id,
            "observations": cluster
        }
