def test_update_requires_nonblank_title(client):
    event_id = client.post("/api/events", json={"title": "Current"}).json["id"]
    response = client.put(f"/api/events/{event_id}", json={"title": "  "})
    assert response.status_code == 400

def test_update_rejects_invalid_severity(client):
    event_id = client.post("/api/events", json={"title": "Current"}).json["id"]
    response = client.put(f"/api/events/{event_id}", json={"title": "New", "severity": "urgent"})
    assert response.status_code == 400
