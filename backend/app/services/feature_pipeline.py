import math
import numpy as np
from typing import Dict, Any, List
from backend.app.services.facility_service import FacilityService
from backend.app.services.baseline_engine import FacilityBaselineEngine

class FeaturePipeline:
    def __init__(self):
        self.facility_service = FacilityService()

    def extract_features(
        self,
        event: Dict[str, Any],
        observations: List[Dict[str, Any]],
        facility: Dict[str, Any] = None,
        weather: Dict[str, Any] = None
    ) -> Dict[str, float]:
        frps = [o.get("frp", 0.0) for o in observations] or [event.get("mean_frp", 10.0)]
        brights = [o.get("brightness", 300.0) for o in observations] or [310.0]

        # 1. Thermal Features
        frp_mean = float(np.mean(frps))
        frp_max = float(np.max(frps))
        frp_median = float(np.median(frps))
        frp_std = float(np.std(frps)) if len(frps) > 1 else 0.0
        frp_p90 = float(np.percentile(frps, 90))
        frp_trend = float(event.get("frp_trend", 0.0))
        brightness_mean = float(np.mean(brights))
        brightness_max = float(np.max(brights))
        thermal_contrast = brightness_max - 295.0  # Approx ambient contrast

        # 2. Temporal Features
        duration_hours = float(event.get("duration_hours", 0.0))
        obs_count = float(len(observations))
        # Persistence ratio: obs per hour of duration (bounded)
        persistence_ratio = min(1.0, obs_count / max(1.0, duration_hours / 6.0))
        recurrence_score = 0.85 if obs_count > 10 else (0.5 if obs_count > 3 else 0.1)

        # 3. Spatial Features
        area_ha = float(event.get("area_ha", 1.0))
        perimeter_m = float(event.get("perimeter_m", math.sqrt(area_ha * 10000.0) * 4.0))
        area_sqm = max(100.0, area_ha * 10000.0)
        # Isoperimetric compactness ratio: 4 * pi * A / P^2
        if "compactness" in event:
            compactness = float(event["compactness"])
        elif perimeter_m > 0:
            compactness = round(min(1.0, (4.0 * math.pi * area_sqm) / (perimeter_m ** 2)), 4)
        else:
            compactness = 0.5
        spread_velocity = round((math.sqrt(area_ha / 100.0) / max(0.5, duration_hours)), 4) if duration_hours > 0 else 0.0

        # 4. Industrial Context Features
        dist_km = float(event.get("distance_to_facility_km", 999.0))
        is_near_facility = 1.0 if dist_km <= 2.0 else 0.0
        inside_polygon = 1.0 if (facility and self.facility_service.is_inside_facility(event.get("centroid_lat", 0.0), event.get("centroid_lon", 0.0), facility)) else 0.0

        # Facility type encoding strictly adhering to feature_schema_v1
        fac_type = (facility.get("facility_type", "none") if facility else "none").lower()
        is_refinery = 1.0 if fac_type in ["refinery", "petrochemical"] else 0.0
        is_coal_mine = 1.0 if fac_type in ["coal_mine", "mine"] else 0.0
        is_power_plant = 1.0 if fac_type == "power_plant" else 0.0
        is_manufacturing = 1.0 if fac_type in ["ceramic_manufacturing", "steel", "cement"] else 0.0

        # 5. Baseline Deviation Features (MAD Z-score)
        if facility and facility.get("baseline_median_frp", 0.0) > 0:
            excursion = FacilityBaselineEngine.calculate_excursion(frp_max, facility)
            frp_zscore = float(excursion.get("frp_zscore", 0.0))
            frp_to_baseline = float(excursion.get("frp_to_baseline_ratio", 1.0))
            # Strict schema condition: Z > 3.0 and frp_max > 25.0
            is_baseline_excursion = 1.0 if (frp_zscore > 3.0 and frp_max > 25.0) else 0.0
        else:
            frp_zscore = 0.0
            frp_to_baseline = 1.0
            is_baseline_excursion = 0.0

        # 6. Environmental & Weather Features
        if weather:
            wind_speed = float(weather.get("wind_speed_10m", 12.0))
            wind_deg = float(weather.get("wind_direction_10m", 180.0))
            temp_2m = float(weather.get("temperature_2m", 28.0))
            rel_humidity = float(weather.get("relative_humidity_2m", 55.0))
        else:
            wind_speed = 12.0
            wind_deg = 180.0
            temp_2m = 28.0
            rel_humidity = 55.0

        # Land cover proxy: 0=water, 1=forest, 2=cropland, 3=urban/industrial, 4=bare
        if inside_polygon or (is_near_facility and dist_km < 0.8):
            landcover_class = 3.0  # Industrial
        elif is_coal_mine and dist_km < 3.0:
            landcover_class = 4.0  # Bare/Mining
        elif dist_km > 5.0 and frp_mean > 50.0:
            landcover_class = 1.0  # Forest/Wildfire
        elif dist_km > 3.0:
            landcover_class = 2.0  # Agricultural cropland
        else:
            landcover_class = 3.0

        # 7. Sensor Agreement
        viirs_count = sum(1 for o in observations if "VIIRS" in o.get("instrument", o.get("source", "")))
        modis_count = sum(1 for o in observations if "MODIS" in o.get("instrument", o.get("source", "")))

        return {
            "frp_mean": round(frp_mean, 2),
            "frp_max": round(frp_max, 2),
            "frp_median": round(frp_median, 2),
            "frp_std": round(frp_std, 2),
            "frp_p90": round(frp_p90, 2),
            "frp_trend": round(frp_trend, 2),
            "brightness_mean": round(brightness_mean, 2),
            "brightness_max": round(brightness_max, 2),
            "thermal_contrast": round(thermal_contrast, 2),
            "duration_hours": round(duration_hours, 2),
            "obs_count": float(obs_count),
            "persistence_ratio": round(persistence_ratio, 2),
            "recurrence_score": round(recurrence_score, 2),
            "area_ha": round(area_ha, 2),
            "compactness": round(compactness, 2),
            "spread_velocity": round(spread_velocity, 2),
            "dist_to_facility_km": round(dist_km, 2),
            "is_near_facility": is_near_facility,
            "inside_facility_polygon": inside_polygon,
            "is_refinery": is_refinery,
            "is_coal_mine": is_coal_mine,
            "is_power_plant": is_power_plant,
            "is_manufacturing": is_manufacturing,
            "frp_zscore": round(frp_zscore, 2),
            "frp_to_baseline": round(frp_to_baseline, 2),
            "is_baseline_excursion": is_baseline_excursion,
            "landcover_class": landcover_class,
            "wind_speed_ms": round(wind_speed, 1),
            "temp_2m_c": round(temp_2m, 1),
            "rel_humidity_pct": round(rel_humidity, 1),
            "viirs_count": float(viirs_count),
            "modis_count": float(modis_count)
        }
