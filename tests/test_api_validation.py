def test_event_api_rejects_invalid_severity(client):
    response = client.post("/api/events", json={"title": "Bad", "severity": "urgent"})
    assert response.status_code == 400
    assert "severity" in response.json["error"]

def test_event_api_rejects_invalid_list_limit(client):
    response = client.get("/api/events?limit=lots")
    assert response.status_code == 400
    assert response.json["error"] == "limit must be an integer"
