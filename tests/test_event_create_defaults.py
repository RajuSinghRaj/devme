def test_event_creation_applies_default_fields(client):
    event_id = client.post("/api/events", json={"title": "Defaults"}).json["id"]
    event = client.get(f"/api/events/{event_id}").json["event"]
    assert event["category"] == "note"
    assert event["severity"] == "normal"
    assert event["details"] == ""
