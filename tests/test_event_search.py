def test_event_search_matches_title(client):
    client.post("/api/events", json={"title": "Restart worker"})
    client.post("/api/events", json={"title": "Update styles"})
    response = client.get("/api/events?q=worker")
    assert response.status_code == 200
    assert [event["title"] for event in response.json["events"]] == ["Restart worker"]


def test_event_search_supports_offset(client):
    for title in ("worker one", "worker two", "worker three"):
        client.post("/api/events", json={"title": title})
    response = client.get("/api/events?q=worker&limit=1&page=2")
    assert response.json["events"][0]["title"] == "worker two"
