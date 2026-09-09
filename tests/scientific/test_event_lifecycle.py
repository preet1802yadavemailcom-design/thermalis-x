import pytest
from datetime import datetime, timedelta
from backend.app.services.event_engine import EventEngine

def test_event_lifecycle_evolution_and_merging():
    engine = EventEngine()
    t0 = datetime(2023, 8, 14, 10, 0)
    
    # Pass 1: Early detection (single observation)
    pass1 = [
        {'latitude': 17.701, 'longitude': 83.256, 'acq_datetime': t0, 'frp': 25.0}
    ]
    clusters_p1 = engine.cluster_observations(pass1)
    assert len(clusters_p1) == 1
    evt1 = engine.construct_event_record('EVT-TEST-LIFECYCLE-01', clusters_p1[0])
    assert evt1['observation_count'] == 1
    assert evt1['mean_frp'] == 25.0
    assert evt1['area_ha'] == 0.5  # Singleton default

    # Pass 2: Escalation 2 hours later (2 additional observations within 0.8 km)
    pass2 = pass1 + [
        {'latitude': 17.703, 'longitude': 83.258, 'acq_datetime': t0 + timedelta(hours=2), 'frp': 95.0},
        {'latitude': 17.702, 'longitude': 83.255, 'acq_datetime': t0 + timedelta(hours=2, minutes=10), 'frp': 110.0}
    ]
    clusters_p2 = engine.cluster_observations(pass2)
    assert len(clusters_p2) == 1
    evt2 = engine.construct_event_record('EVT-TEST-LIFECYCLE-01', clusters_p2[0])
    assert evt2['observation_count'] == 3
    assert evt2['max_frp'] == 110.0
    assert evt2['duration_hours'] > 2.0
    assert evt2['frp_trend'] > 0.0  # Positive growth slope
    assert evt2['area_ha'] > 0.5    # Polygon formed

def test_event_lifecycle_spatial_split():
    engine = EventEngine()
    t0 = datetime(2023, 8, 14, 12, 0)
    
    # 2 observations at site A, 2 observations at site B (3.5 km apart)
    obs = [
        {'latitude': 17.700, 'longitude': 83.250, 'acq_datetime': t0, 'frp': 40.0},
        {'latitude': 17.702, 'longitude': 83.252, 'acq_datetime': t0 + timedelta(minutes=30), 'frp': 45.0},
        {'latitude': 17.735, 'longitude': 83.280, 'acq_datetime': t0, 'frp': 15.0},
        {'latitude': 17.737, 'longitude': 83.282, 'acq_datetime': t0 + timedelta(minutes=30), 'frp': 18.0}
    ]
    clusters = engine.cluster_observations(obs)
    assert len(clusters) == 2
    assert len(clusters[0]) == 2
    assert len(clusters[1]) == 2

def test_event_lifecycle_temporal_split():
    engine = EventEngine()
    t0 = datetime(2023, 8, 14, 12, 0)
    
    # Same location, but separated by 30 hours (> 24h temporal epsilon)
    obs = [
        {'latitude': 17.700, 'longitude': 83.250, 'acq_datetime': t0, 'frp': 40.0},
        {'latitude': 17.700, 'longitude': 83.250, 'acq_datetime': t0 + timedelta(hours=30), 'frp': 45.0}
    ]
    clusters = engine.cluster_observations(obs)
    assert len(clusters) == 2  # Separated into 2 distinct temporal episodes
