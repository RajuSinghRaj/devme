def test_event_detail_returns_404_for_unknown_id(client):
    response = client.get("/api/events/999")
    assert response.status_code == 404
    assert response.json["error"] == "event not found"

def test_event_delete_returns_404_for_unknown_id(client):
    assert client.delete("/api/events/999").status_code == 404
