from events import filter_events

def test_repository_applies_text_category_and_severity_together(client, app):
    client.post("/api/events", json={"title": "Cache issue", "category": "fix", "severity": "high"})
    client.post("/api/events", json={"title": "Cache docs", "category": "note", "severity": "high"})
    client.post("/api/events", json={"title": "Queue issue", "category": "fix", "severity": "low"})
    results = filter_events(app.config["DATABASE"], "Cache", "fix", "high")
    assert [row["title"] for row in results] == ["Cache issue"]


def test_api_combines_search_category_and_severity(client):
    client.post("/api/events", json={"title": "Cache fix", "category": "fix", "severity": "high"})
    client.post("/api/events", json={"title": "Cache note", "category": "note", "severity": "high"})
    response = client.get("/api/events?q=Cache&category=fix&severity=high")
    assert [row["title"] for row in response.json["events"]] == ["Cache fix"]

def test_dashboard_combines_search_category_and_severity(client):
    client.post("/api/events", json={"title": "Cache fix", "category": "fix", "severity": "high"})
    client.post("/api/events", json={"title": "Cache note", "category": "note", "severity": "high"})
    response = client.get("/?q=Cache&category=fix&severity=high")
    assert b"Cache fix" in response.data
    assert b"Cache note" not in response.data


def test_repository_filters_by_date_range(client, app):
    from datetime import datetime, timezone
    from events import filter_events
    client.post("/api/events", json={"title": "Today"})
    today = datetime.now(timezone.utc).date().isoformat()
    assert [row["title"] for row in filter_events(app.config["DATABASE"], from_date=today, to_date=today)] == ["Today"]
    assert filter_events(app.config["DATABASE"], from_date="2000-01-01", to_date="2000-01-02") == []
