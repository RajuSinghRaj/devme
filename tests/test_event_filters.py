from events import filter_events

def test_repository_applies_text_category_and_severity_together(client, app):
    client.post("/api/events", json={"title": "Cache issue", "category": "fix", "severity": "high"})
    client.post("/api/events", json={"title": "Cache docs", "category": "note", "severity": "high"})
    client.post("/api/events", json={"title": "Queue issue", "category": "fix", "severity": "low"})
    results = filter_events(app.config["DATABASE"], "Cache", "fix", "high")
    assert [row["title"] for row in results] == ["Cache issue"]
