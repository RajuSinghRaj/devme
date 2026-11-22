def test_event_api_paginates_newest_first(client):
    for title in ("one", "two", "three"):
        client.post("/api/events", json={"title": title})
    response = client.get("/api/events?page=2&limit=2")
    assert response.json["page"] == 2
    assert [event["title"] for event in response.json["events"]] == ["one"]

def test_event_api_rejects_page_zero(client):
    assert client.get("/api/events?page=0").status_code == 400
