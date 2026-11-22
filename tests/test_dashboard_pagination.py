def test_dashboard_paginates_activity(client):
    for number in range(21):
        client.post("/api/events", json={"title": f"Entry {number}"})
    first = client.get("/")
    second = client.get("/?page=2")
    assert b"Entry 20" in first.data
    assert b"Entry 0" not in first.data
    assert b"Entry 0" in second.data
    assert b"Previous" in second.data
