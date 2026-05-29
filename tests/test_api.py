from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_endpoint(prepared_pipeline):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["api_status"] == "ok"


def test_players_endpoint(prepared_pipeline):
    response = client.get("/players")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_workload_endpoint(prepared_pipeline):
    player_id = client.get("/players").json()[0]["player_id"]
    response = client.get(f"/workload/player/{player_id}")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_injury_risk_endpoint(prepared_pipeline):
    response = client.get("/injury-risk/latest")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_dashboard_page_and_data(prepared_pipeline):
    page = client.get("/dashboard")
    assert page.status_code == 200
    assert "Athlete Monitoring Command Center" in page.text
    data = client.get("/dashboard/data")
    assert data.status_code == 200
    payload = data.json()
    assert len(payload["records"]) > 0
    assert len(payload["players"]) > 0
