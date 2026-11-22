def test_monitor_result_rejects_out_of_range_status_code(client):
    monitor_id = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"}).json["id"]
    response = client.post(f"/api/monitors/{monitor_id}/results", json={"success": True, "status_code": 700})
    assert response.status_code == 400

def test_monitor_result_rejects_negative_response_time(client):
    monitor_id = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"}).json["id"]
    response = client.post(f"/api/monitors/{monitor_id}/results", json={"success": False, "response_ms": -1})
    assert response.status_code == 400
