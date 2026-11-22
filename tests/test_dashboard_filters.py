def test_dashboard_category_filter_limits_entries(client):
    client.post("/events", data={"title": "Repair task", "category": "fix"})
    client.post("/events", data={"title": "Planning note", "category": "note"})
    response = client.get("/?category=fix")
    assert b"Repair task" in response.data
    assert b"Planning note" not in response.data

def test_dashboard_search_can_be_cleared(client):
    response = client.get("/?q=none")
    assert b"Clear filters" in response.data
