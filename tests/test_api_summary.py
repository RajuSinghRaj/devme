def test_summary_reports_event_and_latest_entry(client):
    client.post("/api/events", json={"title": "First"})
    client.post("/api/events", json={"title": "Latest"})
    summary = client.get("/api/summary").json
    assert summary["event_count"] == 2
    assert summary["latest_event"]["title"] == "Latest"


def test_summary_includes_monitor_and_category_totals(client):
    client.post("/api/events", json={"title": "One", "category": "build"})
    client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"})
    summary = client.get("/api/summary").json
    assert summary["event_count"] == 1
    assert summary["category_count"] == 1
    assert summary["monitor_count"] == 1
