def test_dashboard_renders_monitor_section(client):
    response = client.get("/")
    assert b"Monitors" in response.data

def test_dashboard_lists_configured_monitors(client):
    client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"})
    response = client.get("/")
    assert b"Docs" in response.data
    assert b"https://docs.example" in response.data


def test_dashboard_shows_monitor_latest_state(client):
    monitor_id = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"}).json["id"]
    client.post(f"/api/monitors/{monitor_id}/results", json={"success": False, "status_code": 503})
    assert b"DOWN" in client.get("/").data


def test_dashboard_displays_next_check_time(client):
    client.post("/api/monitors", json={"name": "Clock", "url": "https://clock.example"})
    response = client.get("/")
    assert b"Next check" in response.data
