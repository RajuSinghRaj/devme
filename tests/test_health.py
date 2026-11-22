def test_health_reports_service(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok", "service": "DevTrack"}

def test_readiness_reports_database(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json["database"] == "connected"


def test_liveness_endpoint_is_available(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json["status"] == "alive"

def test_uptime_is_nonnegative(client):
    response = client.get("/health/uptime")
    assert response.status_code == 200
    assert response.json["uptime_seconds"] >= 0
