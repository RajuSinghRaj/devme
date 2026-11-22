def test_create_and_read_event(client):
    created = client.post("/api/events", json={"title": "Ship logging"})
    assert created.status_code == 201
    event_id = created.json["id"]
    assert created.headers["Location"] == f"/api/events/{event_id}"
    detail = client.get(created.headers["Location"])
    assert detail.json["event"]["title"] == "Ship logging"

def test_missing_title_is_rejected(client):
    response = client.post("/api/events", json={"title": "  "})
    assert response.status_code == 400
