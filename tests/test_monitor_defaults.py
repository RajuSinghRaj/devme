def test_monitor_creation_uses_default_interval(client):
    monitor_id = client.post("/api/monitors", json={"name": "Default", "url": "https://default.example"}).json["id"]
    monitor = client.get(f"/api/monitors/{monitor_id}").json["monitor"]
    assert monitor["interval_seconds"] == 300
    assert monitor["enabled"] == 1
