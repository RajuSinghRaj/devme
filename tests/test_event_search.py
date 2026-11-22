def test_event_search_matches_title(client):
    client.post("/api/events", json={"title": "Restart worker"})
    client.post("/api/events", json={"title": "Update styles"})
    response = client.get("/api/events?q=worker")
    assert response.status_code == 200
    assert [event["title"] for event in response.json["events"]] == ["Restart worker"]
