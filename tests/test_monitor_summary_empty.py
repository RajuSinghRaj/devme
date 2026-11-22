def test_monitor_summary_has_no_uptime_before_first_check(client):
    monitor_id = client.post("/api/monitors", json={"name": "Fresh", "url": "https://fresh.example"}).json["id"]
    summary = client.get(f"/api/monitors/{monitor_id}/summary").json["summary"]
    assert summary["total_checks"] == 0
    assert summary["uptime_percent"] is None
    assert summary["failure_streak"] == 0
