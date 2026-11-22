def test_event_can_be_edited_from_page(client):
    event_id = client.post("/api/events", json={"title": "Draft"}).json["id"]
    response = client.post(f"/events/{event_id}/edit", data={"title": "Published", "details": "Ready", "severity": "high"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Published" in response.data
    assert client.get(f"/api/events/{event_id}").json["event"]["severity"] == "high"

def test_edit_page_rejects_blank_title(client):
    event_id = client.post("/api/events", json={"title": "Draft"}).json["id"]
    response = client.post(f"/events/{event_id}/edit", data={"title": "  "})
    assert response.status_code == 400
    assert b"Check the title" in response.data
