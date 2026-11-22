def test_monitor_api_lists_empty_collection(client):
    response = client.get("/api/monitors")
    assert response.status_code == 200
    assert response.json == {"monitors": []}


def test_monitor_api_creates_valid_monitor(client):
    response = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"})
    assert response.status_code == 201
    assert client.get("/api/monitors").json["monitors"][0]["name"] == "Docs"

def test_monitor_api_rejects_non_http_url(client):
    response = client.post("/api/monitors", json={"name": "Bad", "url": "file:///etc/passwd"})
    assert response.status_code == 400


def test_monitor_api_pause_and_delete(client):
    monitor_id = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"}).json["id"]
    assert client.patch(f"/api/monitors/{monitor_id}", json={"enabled": False}).json["enabled"] is False
    assert client.delete(f"/api/monitors/{monitor_id}").status_code == 204
    assert client.delete(f"/api/monitors/{monitor_id}").status_code == 404


def test_monitor_api_rejects_interval_below_minimum(client):
    response = client.post("/api/monitors", json={"name": "Fast", "url": "https://example.com", "interval_seconds": 5})
    assert response.status_code == 400
    assert "at least 30" in response.json["error"]


def test_monitor_results_api_records_and_lists_results(client):
    monitor_id = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"}).json["id"]
    recorded = client.post(f"/api/monitors/{monitor_id}/results", json={"success": True, "status_code": 200, "response_ms": 18.3})
    assert recorded.status_code == 201
    results = client.get(f"/api/monitors/{monitor_id}/results").json["results"]
    assert results[0]["status_code"] == 200
    assert results[0]["response_ms"] == 18.3


def test_monitor_summary_api_reports_uptime(client):
    monitor_id = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"}).json["id"]
    client.post(f"/api/monitors/{monitor_id}/results", json={"success": True, "status_code": 200})
    response = client.get(f"/api/monitors/{monitor_id}/summary")
    assert response.json["summary"]["uptime_percent"] == 100.0


def test_monitor_api_retrieves_one_monitor(client):
    monitor_id = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"}).json["id"]
    assert client.get(f"/api/monitors/{monitor_id}").json["monitor"]["name"] == "Docs"
    assert client.get("/api/monitors/999").status_code == 404


def test_monitor_api_updates_metadata(client):
    monitor_id = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"}).json["id"]
    response = client.put(f"/api/monitors/{monitor_id}", json={"name": "Status", "url": "https://status.example", "interval_seconds": 600})
    assert response.status_code == 200
    assert response.json["monitor"]["name"] == "Status"
    assert response.json["monitor"]["interval_seconds"] == 600


def test_monitor_schedule_endpoint_reports_next_run(client):
    monitor_id = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example", "interval_seconds": 600}).json["id"]
    response = client.get(f"/api/monitors/{monitor_id}/schedule")
    assert response.status_code == 200
    assert response.json["interval_seconds"] == 600
    assert response.json["next_check_at"]
    assert response.json["is_due"] is False


def test_monitor_api_rejects_http_url_without_host(client):
    response = client.post("/api/monitors", json={"name": "Bad", "url": "https://"})
    assert response.status_code == 400
    assert "absolute" in response.json["error"]
