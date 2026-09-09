import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any

class DatasetBuilder:
    CLASSES = [
        "IND_ACCIDENT",
        "IND_NORMAL",
        "GAS_FLARE",
        "WILDFIRE",
        "AGRI_BURN",
        "MINE_HEAT",
        "POWER_HEAT",
        "OTHER_NATURAL",
        "FALSE_POSITIVE",
        "UNCERTAIN"
    ]

    @classmethod
    def generate_synthetic_benchmark_data(cls, n_samples: int = 1500, random_seed: int = 42) -> pd.DataFrame:
        np.random.seed(random_seed)
        rows = []

        per_class = n_samples // len(cls.CLASSES)

        for c in cls.CLASSES:
            for i in range(per_class):
                facility_id = f"FAC-REG-{np.random.randint(1, 20):03d}"
                if c == "IND_ACCIDENT":
                    frp_mean = np.random.uniform(70.0, 350.0)
                    frp_max = frp_mean * np.random.uniform(1.3, 2.5)
                    frp_trend = np.random.uniform(15.0, 60.0)
                    dist_km = np.random.uniform(0.05, 0.9)
                    area_ha = np.random.uniform(3.0, 25.0)
                    duration = np.random.uniform(4.0, 48.0)
                    frp_zscore = np.random.uniform(3.5, 15.0)
                    is_excursion = 1.0
                    landcover = 3.0  # Industrial
                    is_refinery = np.random.choice([0.0, 1.0], p=[0.3, 0.7])
                    is_coal_mine = 0.0
                    is_power = 0.0
                elif c == "IND_NORMAL":
                    frp_mean = np.random.uniform(15.0, 45.0)
                    frp_max = frp_mean * np.random.uniform(1.05, 1.25)
                    frp_trend = np.random.uniform(-2.0, 2.0)
                    dist_km = np.random.uniform(0.02, 0.5)
                    area_ha = np.random.uniform(0.5, 2.0)
                    duration = np.random.uniform(12.0, 180.0)
                    frp_zscore = np.random.uniform(-0.5, 1.8)
                    is_excursion = 0.0
                    landcover = 3.0
                    is_refinery = np.random.choice([0.0, 1.0], p=[0.5, 0.5])
                    is_coal_mine = 0.0
                    is_power = 0.0
                elif c == "GAS_FLARE":
                    frp_mean = np.random.uniform(18.0, 35.0)
                    frp_max = frp_mean * np.random.uniform(1.1, 1.4)
                    frp_trend = np.random.uniform(-1.0, 1.0)
                    dist_km = np.random.uniform(0.01, 0.3)
                    area_ha = np.random.uniform(0.2, 0.8)
                    duration = np.random.uniform(24.0, 300.0)
                    frp_zscore = np.random.uniform(-0.2, 1.2)
                    is_excursion = 0.0
                    landcover = 3.0
                    is_refinery = 1.0
                    is_coal_mine = 0.0
                    is_power = 0.0
                elif c == "WILDFIRE":
                    frp_mean = np.random.uniform(40.0, 250.0)
                    frp_max = frp_mean * np.random.uniform(1.5, 3.0)
                    frp_trend = np.random.uniform(5.0, 40.0)
                    dist_km = np.random.uniform(6.0, 45.0)
                    area_ha = np.random.uniform(15.0, 150.0)
                    duration = np.random.uniform(8.0, 72.0)
                    frp_zscore = 0.0
                    is_excursion = 0.0
                    landcover = 1.0  # Forest
                    is_refinery = 0.0
                    is_coal_mine = 0.0
                    is_power = 0.0
                elif c == "AGRI_BURN":
                    frp_mean = np.random.uniform(8.0, 30.0)
                    frp_max = frp_mean * np.random.uniform(1.1, 1.6)
                    frp_trend = np.random.uniform(-5.0, 5.0)
                    dist_km = np.random.uniform(2.5, 20.0)
                    area_ha = np.random.uniform(1.0, 6.0)
                    duration = np.random.uniform(2.0, 7.0)
                    frp_zscore = 0.0
                    is_excursion = 0.0
                    landcover = 2.0  # Cropland
                    is_refinery = 0.0
                    is_coal_mine = 0.0
                    is_power = 0.0
                elif c == "MINE_HEAT":
                    frp_mean = np.random.uniform(10.0, 28.0)
                    frp_max = frp_mean * np.random.uniform(1.05, 1.3)
                    frp_trend = np.random.uniform(-1.0, 1.0)
                    dist_km = np.random.uniform(0.1, 1.5)
                    area_ha = np.random.uniform(1.0, 5.0)
                    duration = np.random.uniform(48.0, 365.0)
                    frp_zscore = np.random.uniform(0.2, 2.0)
                    is_excursion = 0.0
                    landcover = 4.0  # Bare/mining
                    is_refinery = 0.0
                    is_coal_mine = 1.0
                    is_power = 0.0
                elif c == "POWER_HEAT":
                    frp_mean = np.random.uniform(30.0, 65.0)
                    frp_max = frp_mean * np.random.uniform(1.05, 1.25)
                    frp_trend = np.random.uniform(-1.0, 1.0)
                    dist_km = np.random.uniform(0.05, 0.4)
                    area_ha = np.random.uniform(1.0, 3.5)
                    duration = np.random.uniform(72.0, 400.0)
                    frp_zscore = np.random.uniform(-0.4, 1.5)
                    is_excursion = 0.0
                    landcover = 3.0
                    is_refinery = 0.0
                    is_coal_mine = 0.0
                    is_power = 1.0
                elif c == "OTHER_NATURAL":
                    frp_mean = np.random.uniform(5.0, 18.0)
                    frp_max = frp_mean * np.random.uniform(1.0, 1.2)
                    frp_trend = 0.0
                    dist_km = np.random.uniform(10.0, 50.0)
                    area_ha = np.random.uniform(0.5, 2.0)
                    duration = np.random.uniform(10.0, 50.0)
                    frp_zscore = 0.0
                    is_excursion = 0.0
                    landcover = 4.0
                    is_refinery = 0.0
                    is_coal_mine = 0.0
                    is_power = 0.0
                elif c == "FALSE_POSITIVE":
                    frp_mean = np.random.uniform(2.0, 8.0)
                    frp_max = frp_mean * 1.1
                    frp_trend = 0.0
                    dist_km = np.random.uniform(0.5, 10.0)
                    area_ha = 0.5
                    duration = 0.0
                    frp_zscore = 0.0
                    is_excursion = 0.0
                    landcover = 0.0
                    is_refinery = 0.0
                    is_coal_mine = 0.0
                    is_power = 0.0
                else:  # UNCERTAIN
                    frp_mean = np.random.uniform(15.0, 60.0)
                    frp_max = frp_mean * np.random.uniform(1.1, 1.8)
                    frp_trend = np.random.uniform(0.0, 10.0)
                    dist_km = np.random.uniform(1.0, 3.5)
                    area_ha = np.random.uniform(1.5, 8.0)
                    duration = np.random.uniform(4.0, 20.0)
                    frp_zscore = np.random.uniform(1.0, 2.8)
                    is_excursion = 0.0
                    landcover = 3.0
                    is_refinery = 0.0
                    is_coal_mine = 0.0
                    is_power = 0.0

                rows.append({
                    "facility_id": facility_id,
                    "target_class": c,
                    "frp_mean": frp_mean,
                    "frp_max": frp_max,
                    "frp_trend": frp_trend,
                    "dist_to_facility_km": dist_km,
                    "is_near_facility": 1.0 if dist_km <= 2.0 else 0.0,
                    "area_ha": area_ha,
                    "duration_hours": duration,
                    "frp_zscore": frp_zscore,
                    "is_baseline_excursion": is_excursion,
                    "landcover_class": landcover,
                    "is_refinery": is_refinery,
                    "is_coal_mine": is_coal_mine,
                    "is_power_plant": is_power,
                    "compactness": 0.8 if area_ha < 3.0 else 0.3,
                    "persistence_ratio": min(1.0, (duration / 12.0) / max(1.0, duration / 6.0)),
                    "spread_velocity": (np.sqrt(area_ha) / max(0.5, duration))
                })

        df = pd.DataFrame(rows)
        return df
