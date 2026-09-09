import asyncio
import pytest
from datetime import datetime
from backend.app.services.weather_service import WeatherService
from backend.app.services.satellite_evidence import SatelliteEvidenceService
from backend.app.services.firms_ingestion import FIRMSValidator

def test_weather_service_fallback(monkeypatch):
    # Simulate network failure by setting invalid URL
    from backend.app.config import settings
    monkeypatch.setattr(settings, 'WEATHER_BASE_URL', 'http://127.0.0.1:9999/invalid')
    
    weather = asyncio.run(WeatherService.get_weather(17.70, 83.25))
    assert 'temperature_2m' in weather
    assert 'wind_speed_10m' in weather
    assert 'wind_direction_10m' in weather
    assert weather['wind_speed_10m'] > 0.0

def test_satellite_evidence_query():
    scene = asyncio.run(SatelliteEvidenceService.query_sentinel2_scene(17.70, 83.25, datetime(2023, 8, 14, 14, 30)))
    assert scene['sensor'] == 'Sentinel-2 L2A'
    assert 'scene_id' in scene
    assert 'nbr' in scene
    assert 'swir_anomaly' in scene

def test_firms_validator_graceful_rejection():
    # 1. Coordinate out of range
    rec_bad_lat = {'latitude': 195.0, 'longitude': 80.0, 'brightness': 320.0, 'frp': 25.0, 'acq_date': '2023-08-14', 'acq_time': '1200'}
    status, issues = FIRMSValidator.validate_record(rec_bad_lat)
    assert status == 'INVALID'
    assert 'coordinates_out_of_bounds' in issues

    # 2. Negative FRP (Tagged as SUSPECT with impossible_frp)
    rec_neg_frp = {'latitude': 17.0, 'longitude': 80.0, 'brightness': 320.0, 'frp': -10.0, 'acq_date': '2023-08-14', 'acq_time': '1200'}
    status, issues = FIRMSValidator.validate_record(rec_neg_frp)
    assert status == 'SUSPECT'
    assert 'impossible_frp' in issues

    # 3. Brightness temperature physically impossible (Tagged as SUSPECT with suspect_brightness_temperature)
    rec_bad_bright = {'latitude': 17.0, 'longitude': 80.0, 'brightness': 120.0, 'frp': 10.0, 'acq_date': '2023-08-14', 'acq_time': '1200'}
    status, issues = FIRMSValidator.validate_record(rec_bad_bright)
    assert status == 'SUSPECT'
    assert 'suspect_brightness_temperature' in issues
