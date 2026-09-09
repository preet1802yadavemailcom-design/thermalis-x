from datetime import datetime, timedelta
from typing import List, Dict, Any

class ReplayService:
    CASE_STUDIES = [
        {
            "case_id": "CASE-01-VIZAG",
            "title": "HPCL Visakhapatnam Refinery Storage Tank Fire vs Gas Flare",
            "region": "Visakhapatnam, Andhra Pradesh, India",
            "facility_name": "HPCL Visakhapatnam Refinery",
            "description": "Demonstrates normal steady flaring (18-24 MW) escalating into a massive off-stack storage tank fire (320 MW) with baseline violation and critical priority alert.",
            "historical_date": "2023-08-14"
        },
        {
            "case_id": "CASE-02-JHARIA",
            "title": "Jharia Coal Basin Chronic Subsurface Mine Fire",
            "region": "Dhanbad, Jharkhand, India",
            "facility_name": "BCCL Jharia Coal Mines Complex",
            "description": "Demonstrates persistent 180-day chronic thermal recurrence (12-19 MW) in bare mining terrain. Correctly classified as MINE_HEAT without false alarm.",
            "historical_date": "2024-02-20"
        },
        {
            "case_id": "CASE-03-MORBI",
            "title": "Morbi Ceramics Cluster vs Crop Stubble Burning Confounder",
            "region": "Morbi, Gujarat, India",
            "facility_name": "Morbi Ceramic Industrial Zone",
            "description": "Demonstrates heavy agricultural stubble fires 1.4 km outside factory zones. System uses landcover, wind, and baseline envelopes to classify as AGRI_BURN rather than industrial disaster.",
            "historical_date": "2023-11-05"
        }
    ]

    @classmethod
    def get_case_steps(cls, case_id: str) -> List[Dict[str, Any]]:
        if case_id == "CASE-01-VIZAG":
            t0 = datetime(2023, 8, 14, 14, 30)
            return [
                {
                    "step_index": 1,
                    "timestamp": t0.isoformat(),
                    "action": "OBSERVATION_INGESTED",
                    "description": "VIIRS NOAA-20 detection at HPCL Vizag flare stack (19.4 MW). FRP matches historical baseline median.",
                    "event_id": "EVT-VIZAG-20230814-01",
                    "active_observations_count": 1,
                    "current_frp": 19.4,
                    "current_area_ha": 0.5,
                    "current_class": "GAS_FLARE",
                    "current_priority": "INFORMATIONAL",
                    "alert_triggered": False
                },
                {
                    "step_index": 2,
                    "timestamp": (t0 + timedelta(hours=3)).isoformat(),
                    "action": "THERMAL_SURGE_DETECTED",
                    "description": "VIIRS NOAA-21 pass detects rapid thermal surge to 142.0 MW. Off-stack location detected 280m south of flare stack.",
                    "event_id": "EVT-VIZAG-20230814-01",
                    "active_observations_count": 3,
                    "current_frp": 142.0,
                    "current_area_ha": 3.8,
                    "current_class": "IND_ACCIDENT",
                    "current_priority": "WARNING",
                    "alert_triggered": True
                },
                {
                    "step_index": 3,
                    "timestamp": (t0 + timedelta(hours=6)).isoformat(),
                    "action": "CRITICAL_EXCURSION_PEAK",
                    "description": "MODIS Aqua & VIIRS pass detects catastrophic peak at 328.5 MW with footprint expanding to 12.4 ha. Stark baseline MAD z-score (14.2).",
                    "event_id": "EVT-VIZAG-20230814-01",
                    "active_observations_count": 8,
                    "current_frp": 328.5,
                    "current_area_ha": 12.4,
                    "current_class": "IND_ACCIDENT",
                    "current_priority": "CRITICAL",
                    "alert_triggered": True
                },
                {
                    "step_index": 4,
                    "timestamp": (t0 + timedelta(hours=14)).isoformat(),
                    "action": "CONTAINMENT_AND_DECAY",
                    "description": "Thermal suppression underway. FRP decays to 45.0 MW. Footprint stabilizing. Analyst confirms industrial storage incident.",
                    "event_id": "EVT-VIZAG-20230814-01",
                    "active_observations_count": 12,
                    "current_frp": 45.0,
                    "current_area_ha": 8.0,
                    "current_class": "IND_ACCIDENT",
                    "current_priority": "WATCH",
                    "alert_triggered": False
                }
            ]
        elif case_id == "CASE-02-JHARIA":
            t0 = datetime(2024, 2, 20, 10, 15)
            return [
                {
                    "step_index": 1,
                    "timestamp": t0.isoformat(),
                    "action": "CHRONIC_HOTSPOT_OBSERVED",
                    "description": "VIIRS detection in BCCL Block II open-cast pit (14.2 MW). Persistent chronic thermal history detected over 180 days.",
                    "event_id": "EVT-JHARIA-20240220-01",
                    "active_observations_count": 1,
                    "current_frp": 14.2,
                    "current_area_ha": 1.2,
                    "current_class": "MINE_HEAT",
                    "current_priority": "INFORMATIONAL",
                    "alert_triggered": False
                },
                {
                    "step_index": 2,
                    "timestamp": (t0 + timedelta(hours=12)).isoformat(),
                    "action": "STABLE_PERIMETER_MONITORED",
                    "description": "Night-time VIIRS swath confirms stationary FRP (15.1 MW). Zero perimeter dilation. Classified safely as MINE_HEAT.",
                    "event_id": "EVT-JHARIA-20240220-01",
                    "active_observations_count": 2,
                    "current_frp": 15.1,
                    "current_area_ha": 1.2,
                    "current_class": "MINE_HEAT",
                    "current_priority": "INFORMATIONAL",
                    "alert_triggered": False
                }
            ]
        else:
            t0 = datetime(2023, 11, 5, 13, 0)
            return [
                {
                    "step_index": 1,
                    "timestamp": t0.isoformat(),
                    "action": "PROXIMATE_FIRE_DETECTED",
                    "description": "VIIRS detects 24.5 MW hotspot 1.4 km from Morbi ceramic kilns. Potential confounder triage initiated.",
                    "event_id": "EVT-MORBI-20231105-01",
                    "active_observations_count": 1,
                    "current_frp": 24.5,
                    "current_area_ha": 2.0,
                    "current_class": "AGRI_BURN",
                    "current_priority": "INFORMATIONAL",
                    "alert_triggered": False
                },
                {
                    "step_index": 2,
                    "timestamp": (t0 + timedelta(hours=4)).isoformat(),
                    "action": "AGRICULTURAL_BURN_CONFIRMED",
                    "description": "ESA WorldCover cropland verification and downwind smoke drift confirm agricultural stubble burning outside industrial bounds.",
                    "event_id": "EVT-MORBI-20231105-01",
                    "active_observations_count": 2,
                    "current_frp": 18.0,
                    "current_area_ha": 2.5,
                    "current_class": "AGRI_BURN",
                    "current_priority": "INFORMATIONAL",
                    "alert_triggered": False
                }
            ]
