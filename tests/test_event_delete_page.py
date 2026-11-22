def test_event_can_be_deleted_from_detail_page(client):
    event_id = client.post("/api/events", json={"title": "Temporary"}).json["id"]
    response = client.post(f"/events/{event_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert b"Temporary" not in response.data
    assert client.get(f"/api/events/{event_id}").status_code == 404

def test_delete_page_returns_not_found_for_missing_event(client):
    assert client.post("/events/999/delete").status_code == 404
