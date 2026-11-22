def test_empty_event_api_returns_empty_list(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    assert response.json["events"] == []
    assert response.json["page"] == 1
