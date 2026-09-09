import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from datetime import datetime, timedelta
from backend.app.db.session import SessionLocal, engine
from backend.app.db.base import Base
from backend.app.db.models import Facility, Event, Observation, SatelliteEvidence, Alert
from backend.app.services.facility_service import FacilityService
from backend.app.services.baseline_engine import FacilityBaselineEngine
from backend.app.services.feature_pipeline import FeaturePipeline
from backend.app.services.ml_service import MLClassificationService
from backend.app.services.risk_engine import RiskPriorityEngine
from backend.app.services.alert_service import AlertService

def seed():
    print("Initializing schema and seeding THERMALIS-X operational database...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear previous seed data
    db.query(Alert).delete()
    db.query(SatelliteEvidence).delete()
    db.query(Observation).delete()
    db.query(Event).delete()
    db.query(Facility).delete()
    db.commit()

    # 1. Seed Facilities
    facility_service = FacilityService()
    for fac_data in facility_service.CURATED_FACILITIES:
        fac = Facility(**fac_data)
        db.add(fac)
    db.commit()
    print(f"Seeded {len(facility_service.CURATED_FACILITIES)} mission-critical industrial facilities.")

    # 2. Seed Replay Scenarios & Active Events
    # Scenario 1: HPCL Vizag Storage Tank Fire (Critical Accident)
    t_base = datetime(2023, 8, 14, 14, 30)
    ev_vizag = Event(
        id="EVT-VIZAG-20230814-01",
        status="ACTIVE",
        first_seen=t_base,
        last_seen=t_base + timedelta(hours=6),
        duration_hours=6.0,
        observation_count=8,
        centroid_lat=17.7025,
        centroid_lon=83.2580,
        area_ha=12.4,
        max_frp=328.5,
        mean_frp=145.2,
        total_fre_mj=3136320.0,
        frp_trend=45.2,
        source_class="IND_ACCIDENT",
        abnormality_state="CRITICAL_FIRE",
        abnormality_score=0.95,
        conformal_set_json=json.dumps(["IND_ACCIDENT"]),
        raw_probabilities_json=json.dumps({"IND_ACCIDENT": 0.88, "GAS_FLARE": 0.08, "IND_NORMAL": 0.03, "WILDFIRE": 0.01}),
        calibrated_prob=0.92,
        uncertainty=0.18,
        abstained=False,
        priority="CRITICAL",
        priority_score=94.5,
        nearest_facility_id="FAC-VIZAG-001",
        distance_to_facility_km=0.18,
        lineage_type="CONTINUATION",
        convex_hull_geojson=json.dumps({
            "type": "Polygon",
            "coordinates": [[[83.253, 17.698], [83.264, 17.698], [83.264, 17.708], [83.253, 17.708], [83.253, 17.698]]]
        }),
        shap_explanation_json=json.dumps({
            "predicted_class": "IND_ACCIDENT",
            "confidence": 0.92,
            "top_contributions": [
                {"feature": "frp_zscore", "value": "14.2", "impact": "+0.45", "reason": "Current FRP of 328.5 MW starkly exceeds HPCL facility baseline median (18.5 MW) by 14.2 robust MAD standard deviations"},
                {"feature": "dist_to_facility_km", "value": "0.18 km", "impact": "+0.32", "reason": "Inside hazardous fuel tank farm containment perimeter"},
                {"feature": "frp_trend", "value": "+45.2 MW/hr", "impact": "+0.24", "reason": "Violent kinetic escalation over consecutive satellite revisits"}
            ]
        })
    )
    db.add(ev_vizag)

    # Observations for Vizag
    vizag_obs = [
        Observation(id="OBS-VIZAG-01", source="VIIRS_NOAA20_NRT", satellite="NOAA-20", instrument="VIIRS", latitude=17.7012, longitude=83.2568, acq_datetime=t_base, frp=19.4, brightness=328.5, confidence="high", event_id=ev_vizag.id, raw_hash="hash_vizag_01"),
        Observation(id="OBS-VIZAG-02", source="VIIRS_NOAA21_NRT", satellite="NOAA-21", instrument="VIIRS", latitude=17.7020, longitude=83.2575, acq_datetime=t_base + timedelta(hours=3), frp=142.0, brightness=365.2, confidence="high", event_id=ev_vizag.id, raw_hash="hash_vizag_02"),
        Observation(id="OBS-VIZAG-03", source="MODIS_NRT", satellite="Aqua", instrument="MODIS", latitude=17.7028, longitude=83.2582, acq_datetime=t_base + timedelta(hours=6), frp=328.5, brightness=415.8, confidence="nominal", event_id=ev_vizag.id, raw_hash="hash_vizag_03")
    ]
    db.add_all(vizag_obs)

    # Satellite Evidence for Vizag
    sat_vizag = SatelliteEvidence(
        id="SAT-VIZAG-01",
        event_id=ev_vizag.id,
        sensor="Sentinel-2 L2A",
        scene_id="S2B_MSIL2A_20230814_T44QND",
        acquisition_time=t_base + timedelta(hours=5),
        cloud_coverage=8.5,
        status="AVAILABLE",
        ndvi=0.12,
        nbr=-0.58,
        swir_anomaly=4.2,
        thumbnail_url="/static/evidence/vizag_swir_thermal_plume.jpg",
        provenance_metadata_json=json.dumps({"source": "Copernicus STAC AWS", "processing_level": "Level-2A BOA Reflectance"})
    )
    db.add(sat_vizag)

    # Alert for Vizag
    alert_vizag = Alert(
        id="ALT-VIZAG-001",
        event_id=ev_vizag.id,
        severity="CRITICAL",
        status="NEW",
        title="CRITICAL: Confirmed Industrial Fire Excursion at HPCL Visakhapatnam Refinery",
        description="Event EVT-VIZAG-20230814-01 exhibits max FRP of 328.5 MW (14.2x MAD baseline excursion) within fuel storage sector.",
        priority_score=94.5,
        facility_name="HPCL Visakhapatnam Refinery",
        recommended_action="Immediate dispatch of NDRF / State Industrial Fire Brigade. Trigger foam deluge and refinery emergency cutoff."
    )
    db.add(alert_vizag)

    # Scenario 2: Jharia Coal Basin (Chronic Mine Heat)
    t_jharia = datetime(2024, 2, 20, 10, 15)
    ev_jharia = Event(
        id="EVT-JHARIA-20240220-01",
        status="ACTIVE",
        first_seen=t_jharia,
        last_seen=t_jharia + timedelta(hours=18),
        duration_hours=18.0,
        observation_count=5,
        centroid_lat=23.7515,
        centroid_lon=86.4155,
        area_ha=2.2,
        max_frp=16.5,
        mean_frp=13.8,
        total_fre_mj=894240.0,
        frp_trend=0.2,
        source_class="MINE_HEAT",
        abnormality_state="NORMAL",
        abnormality_score=0.05,
        conformal_set_json=json.dumps(["MINE_HEAT"]),
        raw_probabilities_json=json.dumps({"MINE_HEAT": 0.89, "IND_NORMAL": 0.06, "WILDFIRE": 0.03, "IND_ACCIDENT": 0.02}),
        calibrated_prob=0.91,
        uncertainty=0.15,
        abstained=False,
        priority="INFORMATIONAL",
        priority_score=22.0,
        nearest_facility_id="FAC-JHARIA-002",
        distance_to_facility_km=0.12,
        lineage_type="INITIAL",
        convex_hull_geojson=json.dumps({
            "type": "Polygon",
            "coordinates": [[[86.410, 23.748], [86.422, 23.748], [86.422, 23.756], [86.410, 23.756], [86.410, 23.748]]]
        }),
        shap_explanation_json=json.dumps({
            "predicted_class": "MINE_HEAT",
            "confidence": 0.91,
            "top_contributions": [
                {"feature": "is_coal_mine", "value": "BCCL Coal Tag", "impact": "+0.48", "reason": "Location within known open-cast coal seam fire polygon"},
                {"feature": "spread_velocity", "value": "0.08 km/h", "impact": "+0.28", "reason": "Stationary smoldering characteristic of subsurface coal seams"},
                {"feature": "persistence_ratio", "value": "0.85", "impact": "+0.20", "reason": "Continuous 180-day thermal recurrence without perimeter expansion"}
            ]
        })
    )
    db.add(ev_jharia)

    # Scenario 3: Morbi Agricultural Burning Confounder
    t_morbi = datetime(2023, 11, 5, 13, 0)
    ev_morbi = Event(
        id="EVT-MORBI-20231105-01",
        status="ACTIVE",
        first_seen=t_morbi,
        last_seen=t_morbi + timedelta(hours=4),
        duration_hours=4.0,
        observation_count=2,
        centroid_lat=22.8420,
        centroid_lon=70.8550,
        area_ha=3.1,
        max_frp=26.0,
        mean_frp=21.5,
        total_fre_mj=309600.0,
        frp_trend=-1.2,
        source_class="AGRI_BURN",
        abnormality_state="NORMAL",
        abnormality_score=0.05,
        conformal_set_json=json.dumps(["AGRI_BURN"]),
        raw_probabilities_json=json.dumps({"AGRI_BURN": 0.84, "WILDFIRE": 0.10, "IND_ACCIDENT": 0.04, "IND_NORMAL": 0.02}),
        calibrated_prob=0.86,
        uncertainty=0.22,
        abstained=False,
        priority="INFORMATIONAL",
        priority_score=18.5,
        nearest_facility_id="FAC-MORBI-003",
        distance_to_facility_km=2.45,
        lineage_type="INITIAL",
        convex_hull_geojson=json.dumps({
            "type": "Polygon",
            "coordinates": [[[70.848, 22.836], [70.862, 22.836], [70.862, 22.848], [70.848, 22.848], [70.848, 22.836]]]
        }),
        shap_explanation_json=json.dumps({
            "predicted_class": "AGRI_BURN",
            "confidence": 0.86,
            "top_contributions": [
                {"feature": "landcover_class", "value": "Cropland", "impact": "+0.42", "reason": "ESA WorldCover agricultural stubble burning classification"},
                {"feature": "dist_to_facility_km", "value": "2.45 km", "impact": "+0.30", "reason": "Outside Morbi ceramic industrial cluster boundary envelope"},
                {"feature": "duration_hours", "value": "4.0 hrs", "impact": "+0.18", "reason": "Transient diurnal post-harvest burn cycle"}
            ]
        })
    )
    db.add(ev_morbi)

    # Scenario 4: IOCL Paradeep Petrochemicals Normal Operational Flare
    t_paradeep = datetime(2024, 3, 1, 21, 0)
    ev_paradeep = Event(
        id="EVT-PARADEEP-20240301-01",
        status="ACTIVE",
        first_seen=t_paradeep,
        last_seen=t_paradeep + timedelta(hours=12),
        duration_hours=12.0,
        observation_count=4,
        centroid_lat=20.2855,
        centroid_lon=86.6660,
        area_ha=0.4,
        max_frp=28.2,
        mean_frp=24.5,
        total_fre_mj=1058400.0,
        frp_trend=0.1,
        source_class="GAS_FLARE",
        abnormality_state="NORMAL",
        abnormality_score=0.05,
        conformal_set_json=json.dumps(["GAS_FLARE"]),
        raw_probabilities_json=json.dumps({"GAS_FLARE": 0.91, "IND_NORMAL": 0.05, "IND_ACCIDENT": 0.03, "UNCERTAIN": 0.01}),
        calibrated_prob=0.93,
        uncertainty=0.12,
        abstained=False,
        priority="INFORMATIONAL",
        priority_score=26.0,
        nearest_facility_id="FAC-PARADEEP-004",
        distance_to_facility_km=0.08,
        lineage_type="INITIAL",
        convex_hull_geojson=json.dumps({
            "type": "Point",
            "coordinates": [86.6660, 20.2855]
        }),
        shap_explanation_json=json.dumps({
            "predicted_class": "GAS_FLARE",
            "confidence": 0.93,
            "top_contributions": [
                {"feature": "is_refinery", "value": "Petrochemical Tag", "impact": "+0.46", "reason": "Co-located with IOCL continuous flare stack header"},
                {"feature": "compactness", "value": "Point Source", "impact": "+0.28", "reason": "Zero spatial perimeter dilation (0.4 ha)"},
                {"feature": "frp_zscore", "value": "0.76", "impact": "+0.22", "reason": "FRP of 28.2 MW matches historical P10-P90 operational envelope"}
            ]
        })
    )
    db.add(ev_paradeep)

    # Scenario 5: Tata Steel Works Blast Furnace Heat
    t_tata = datetime(2024, 3, 2, 8, 30)
    ev_tata = Event(
        id="EVT-TATA-20240302-01",
        status="ACTIVE",
        first_seen=t_tata,
        last_seen=t_tata + timedelta(hours=24),
        duration_hours=24.0,
        observation_count=6,
        centroid_lat=22.7955,
        centroid_lon=86.2060,
        area_ha=1.8,
        max_frp=36.0,
        mean_frp=31.2,
        total_fre_mj=2695680.0,
        frp_trend=-0.1,
        source_class="IND_NORMAL",
        abnormality_state="NORMAL",
        abnormality_score=0.05,
        conformal_set_json=json.dumps(["IND_NORMAL"]),
        raw_probabilities_json=json.dumps({"IND_NORMAL": 0.88, "GAS_FLARE": 0.06, "POWER_HEAT": 0.04, "IND_ACCIDENT": 0.02}),
        calibrated_prob=0.90,
        uncertainty=0.14,
        abstained=False,
        priority="INFORMATIONAL",
        priority_score=24.5,
        nearest_facility_id="FAC-TATASTEEL-005",
        distance_to_facility_km=0.15,
        lineage_type="INITIAL",
        convex_hull_geojson=json.dumps({
            "type": "Polygon",
            "coordinates": [[[86.200, 22.790], [86.212, 22.790], [86.212, 22.802], [86.200, 22.802], [86.200, 22.790]]]
        }),
        shap_explanation_json=json.dumps({
            "predicted_class": "IND_NORMAL",
            "confidence": 0.90,
            "top_contributions": [
                {"feature": "is_manufacturing", "value": "Steel Works Tag", "impact": "+0.44", "reason": "Co-located with blast furnace and basic oxygen steelmaking shop"},
                {"feature": "frp_zscore", "value": "0.58", "impact": "+0.30", "reason": "FRP strictly within normal 32.0 MW steelmaking baseline"},
                {"feature": "persistence_ratio", "value": "0.92", "impact": "+0.20", "reason": "Continuous 24/7 industrial thermal operation"}
            ]
        })
    )
    db.add(ev_tata)

    db.commit()
    db.close()
    print("Database successfully seeded with 5 diverse, high-fidelity operational test scenarios.")

if __name__ == "__main__":
    seed()
