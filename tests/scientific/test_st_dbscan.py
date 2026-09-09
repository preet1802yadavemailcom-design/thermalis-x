import pytest
from datetime import datetime, timedelta
from backend.app.services.event_engine import EventEngine

def test_st_dbscan_clustering_core_and_density():
    ee = EventEngine(spatial_eps_km=1.25, temporal_eps_hours=24.0, min_pts=2)
    t0 = datetime(2023, 8, 14, 12, 0)

    # 3 points tightly clustered in space (<0.5 km) and time (<2 hours)
    obs = [
        {"latitude": 17.701, "longitude": 83.256, "acq_datetime": t0, "frp": 25.0},
        {"latitude": 17.703, "longitude": 83.258, "acq_datetime": t0 + timedelta(hours=1), "frp": 60.0},
        {"latitude": 17.702, "longitude": 83.257, "acq_datetime": t0 + timedelta(hours=2), "frp": 40.0},
        # 1 isolated distant point (>10 km away)
        {"latitude": 17.850, "longitude": 83.350, "acq_datetime": t0 + timedelta(hours=3), "frp": 15.0}
    ]

    clusters = ee.cluster_observations(obs)
    # Expect 2 clusters: the core 3-point cluster and the 1-point singleton
    assert len(clusters) == 2
    main_cluster = max(clusters, key=len)
    assert len(main_cluster) == 3
    distant_cluster = min(clusters, key=len)
    assert len(distant_cluster) == 1

def test_st_dbscan_temporal_isolation():
    ee = EventEngine(spatial_eps_km=1.25, temporal_eps_hours=24.0, min_pts=2)
    t0 = datetime(2023, 8, 14, 12, 0)

    # Identical coordinates, but separated by 48 hours (> 24 hours eps_t)
    obs = [
        {"latitude": 17.701, "longitude": 83.256, "acq_datetime": t0, "frp": 30.0},
        {"latitude": 17.701, "longitude": 83.256, "acq_datetime": t0 + timedelta(hours=48), "frp": 35.0}
    ]

    clusters = ee.cluster_observations(obs)
    assert len(clusters) == 2  # Separated by temporal window

def test_st_dbscan_chain_linking_prevention():
    # If points A, B, C, D form a sparse chain where each has at most 3 neighbors (insufficient for min_pts=4 core),
    # ST-DBSCAN prevents unchecked single-linkage propagation
    ee = EventEngine(spatial_eps_km=1.0, temporal_eps_hours=12.0, min_pts=4)
    t0 = datetime(2023, 8, 14, 12, 0)

    obs = [
        {"latitude": 17.700, "longitude": 83.250, "acq_datetime": t0, "frp": 20.0},
        {"latitude": 17.708, "longitude": 83.250, "acq_datetime": t0 + timedelta(hours=1), "frp": 20.0},  # ~0.89 km from A
        {"latitude": 17.716, "longitude": 83.250, "acq_datetime": t0 + timedelta(hours=2), "frp": 20.0},  # ~0.89 km from B
        {"latitude": 17.724, "longitude": 83.250, "acq_datetime": t0 + timedelta(hours=3), "frp": 20.0},  # ~0.89 km from C
    ]

    clusters = ee.cluster_observations(obs)
    # Under min_pts=4, none of the points have 4 neighbors in eps_s=1.0km, so no mega-cluster of size 4 is formed
    assert all(len(c) < 4 for c in clusters)

def test_event_record_timestamps_and_compactness():
    ee = EventEngine()
    t0 = datetime(2023, 8, 14, 12, 0)
    obs = [
        {"latitude": 17.701, "longitude": 83.256, "acq_datetime": t0, "frp": 20.0},
        {"latitude": 17.704, "longitude": 83.259, "acq_datetime": t0 + timedelta(hours=3), "frp": 145.0}, # Peak FRP
        {"latitude": 17.702, "longitude": 83.257, "acq_datetime": t0 + timedelta(hours=6), "frp": 50.0}
    ]

    ev = ee.construct_event_record("EVT-TEST-001", obs)
    assert ev["observation_count"] == 3
    assert ev["max_frp"] == 145.0
    assert ev["duration_hours"] == 6.0
    assert ev["onset_timestamp"] == t0.isoformat()
    assert ev["peak_timestamp"] == (t0 + timedelta(hours=3)).isoformat()
    assert ev["end_timestamp"] == (t0 + timedelta(hours=6)).isoformat()
    assert 0.0 < ev["compactness"] <= 1.0
