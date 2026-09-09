import pytest
from datetime import datetime, timedelta
from backend.app.services.event_engine import EventEngine

def test_event_clustering():
    engine = EventEngine()
    t0 = datetime(2023, 8, 14, 12, 0)
    # 3 observations clustered within 1 km and 2 hours
    obs_list = [
        {"latitude": 17.701, "longitude": 83.256, "acq_datetime": t0, "frp": 20.0},
        {"latitude": 17.703, "longitude": 83.258, "acq_datetime": t0 + timedelta(hours=1), "frp": 35.0},
        {"latitude": 17.702, "longitude": 83.257, "acq_datetime": t0 + timedelta(hours=2), "frp": 50.0},
        # 1 distant observation 20 km away
        {"latitude": 17.850, "longitude": 83.400, "acq_datetime": t0, "frp": 15.0}
    ]

    clusters = engine.cluster_observations(obs_list)
    assert len(clusters) == 2
    assert len(clusters[0]) == 3
    assert len(clusters[1]) == 1

def test_event_construction():
    engine = EventEngine()
    t0 = datetime(2023, 8, 14, 12, 0)
    cluster = [
        {"latitude": 17.701, "longitude": 83.256, "acq_datetime": t0, "frp": 20.0},
        {"latitude": 17.703, "longitude": 83.258, "acq_datetime": t0 + timedelta(hours=2), "frp": 60.0}
    ]
    event = engine.construct_event_record("EVT-TEST-001", cluster)
    assert event["id"] == "EVT-TEST-001"
    assert event["observation_count"] == 2
    assert event["max_frp"] == 60.0
    assert event["duration_hours"] == 2.0
