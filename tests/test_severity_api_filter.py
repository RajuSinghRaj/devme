def test_api_can_filter_events_by_severity(client):
    client.post("/api/events", json={"title": "Urgent", "severity": "high"})
    client.post("/api/events", json={"title": "Routine", "severity": "low"})
    response = client.get("/api/events?severity=high")
    assert [row["title"] for row in response.json["events"]] == ["Urgent"]
