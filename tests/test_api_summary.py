def test_summary_reports_event_and_latest_entry(client):
    client.post("/api/events", json={"title": "First"})
    client.post("/api/events", json={"title": "Latest"})
    summary = client.get("/api/summary").json
    assert summary["event_count"] == 2
    assert summary["latest_event"]["title"] == "Latest"
