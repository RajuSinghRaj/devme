def test_event_detail_page_shows_entry_content(client):
    event_id = client.post("/api/events", json={"title": "Full entry", "details": "Long-form notes", "category": "decision"}).json["id"]
    response = client.get(f"/events/{event_id}")
    assert response.status_code == 200
    assert b"Full entry" in response.data
    assert b"Long-form notes" in response.data

def test_missing_event_detail_page_is_not_found(client):
    assert client.get("/events/999").status_code == 404


def test_detail_page_offers_edit_and_delete_actions(client):
    event_id = client.post("/api/events", json={"title": "Actionable"}).json["id"]
    response = client.get(f"/events/{event_id}")
    assert b"Edit entry" in response.data
    assert b"Delete entry" in response.data
