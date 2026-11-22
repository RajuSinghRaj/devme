def test_event_update_and_delete(client):
    event_id = client.post("/api/events", json={"title": "Draft"}).json["id"]
    updated = client.put(f"/api/events/{event_id}", json={"title": "Published"})
    assert updated.status_code == 200
    assert client.get(f"/api/events/{event_id}").json["event"]["title"] == "Published"
    assert client.delete(f"/api/events/{event_id}").status_code == 204
    assert client.get(f"/api/events/{event_id}").status_code == 404
