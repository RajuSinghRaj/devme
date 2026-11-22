def test_health_reports_service(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok", "service": "DevTrack"}

def test_readiness_reports_database(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json["database"] == "connected"
