def test_dashboard_filters_by_severity(client):
    client.post("/events", data={"title": "Critical fix", "severity": "high"})
    client.post("/events", data={"title": "Small note", "severity": "low"})
    response = client.get("/?severity=high")
    assert b"Critical fix" in response.data
    assert b"Small note" not in response.data
