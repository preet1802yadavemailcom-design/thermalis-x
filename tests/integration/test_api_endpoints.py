import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"
    assert "components" in data

def test_events_list():
    response = client.get("/api/v1/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 1
    # Check Vizag event
    vizag = next((e for e in events if "VIZAG" in e["id"]), None)
    assert vizag is not None
    assert vizag["source_class"] == "IND_ACCIDENT"
    assert vizag["priority"] == "CRITICAL"

def test_event_detail():
    response = client.get("/api/v1/events/EVT-VIZAG-20230814-01")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "EVT-VIZAG-20230814-01"
    assert data["shap_explanation"] is not None

def test_facilities_list():
    response = client.get("/api/v1/facilities")
    assert response.status_code == 200
    facs = response.json()
    assert len(facs) >= 3

def test_alerts_list():
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    alerts = response.json()
    assert len(alerts) >= 1

def test_replay_cases():
    response = client.get("/api/v1/replay/cases")
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) == 3

def test_replay_steps():
    response = client.get("/api/v1/replay/cases/CASE-01-VIZAG/steps")
    assert response.status_code == 200
    steps = response.json()
    assert len(steps) == 4

def test_event_response_plan_endpoint():
    response = client.get("/api/v1/events/EVT-VIZAG-20230814-01/response-plan")
    assert response.status_code == 200
    data = response.json()
    assert "isolation_radius_meters" in data
    assert "recommended_action" in data
    assert "dispatched_agencies" in data

def test_event_ics_201_briefing_endpoint():
    response = client.get("/api/v1/events/EVT-VIZAG-20230814-01/ics-201")
    assert response.status_code == 200
    data = response.json()
    assert data["form_type"] == "ICS-201 Incident Briefing"
    assert "formatted_briefing" in data
    assert "safety_perimeters" in data

