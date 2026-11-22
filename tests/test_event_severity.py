from events import list_events_by_severity

def test_repository_filters_events_by_severity(client, app):
    client.post("/api/events", json={"title": "Urgent", "severity": "high"})
    client.post("/api/events", json={"title": "Routine", "severity": "low"})
    rows = list_events_by_severity(app.config["DATABASE"], "high")
    assert [row["title"] for row in rows] == ["Urgent"]
