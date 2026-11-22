def test_new_monitor_has_empty_result_history(client):
    monitor_id = client.post("/api/monitors", json={"name": "Fresh", "url": "https://fresh.example"}).json["id"]
    response = client.get(f"/api/monitors/{monitor_id}/results")
    assert response.status_code == 200
    assert response.json["results"] == []
