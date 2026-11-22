def test_categories_endpoint_lists_used_categories(client):
    client.post("/api/events", json={"title": "Repair", "category": "fix"})
    client.post("/api/events", json={"title": "Plan", "category": "note"})
    assert client.get("/api/categories").json["categories"] == ["fix", "note"]

def test_category_filter_returns_matching_events(client):
    client.post("/api/events", json={"title": "Repair", "category": "fix"})
    client.post("/api/events", json={"title": "Plan", "category": "note"})
    rows = client.get("/api/events?category=fix").json["events"]
    assert [row["title"] for row in rows] == ["Repair"]
