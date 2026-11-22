def test_monitor_detail_displays_recent_results(client):
    monitor_id = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"}).json["id"]
    client.post(f"/api/monitors/{monitor_id}/results", json={"success": True, "status_code": 200, "response_ms": 12})
    response = client.get(f"/monitors/{monitor_id}")
    assert response.status_code == 200
    assert b"Check history" in response.data
    assert b"Success" in response.data

def test_unknown_monitor_detail_returns_404(client):
    assert client.get("/monitors/999").status_code == 404


def test_monitor_detail_shows_check_schedule(client):
    monitor_id = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"}).json["id"]
    response = client.get(f"/monitors/{monitor_id}")
    assert b"Next check" in response.data


def test_monitor_detail_escapes_monitor_name(client):
    client.post("/api/monitors", json={"name": "<script>alert(1)</script>", "url": "https://safe.example"})
    response = client.get("/")
    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;" in response.data
