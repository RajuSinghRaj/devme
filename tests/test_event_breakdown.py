from events import event_breakdown

def test_event_breakdown_groups_categories_and_severity(client, app):
    client.post("/api/events", json={"title": "Build", "category": "build", "severity": "high"})
    client.post("/api/events", json={"title": "Note", "category": "note", "severity": "low"})
    result = event_breakdown(app.config["DATABASE"])
    assert result["categories"] == {"build": 1, "note": 1}
    assert result["severities"] == {"high": 1, "low": 1}


def test_event_breakdown_endpoint_returns_grouped_counts(client):
    client.post("/api/events", json={"title": "Build", "category": "build", "severity": "high"})
    response = client.get("/api/events/breakdown")
    assert response.status_code == 200
    assert response.json["categories"]["build"] == 1
