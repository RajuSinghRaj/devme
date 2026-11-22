def test_version_endpoint_returns_service_version(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json == {"name": "DevTrack", "version": "0.1.0"}
