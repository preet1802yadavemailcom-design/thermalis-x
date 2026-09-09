import math
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
            from shapely.geometry import shape, Point
            geom = json.loads(facility["footprint_geojson"])
            poly = shape(geom)
            pt = Point(lon, lat)
            return bool(poly.contains(pt) or poly.touches(pt))
        except Exception:
            return False
