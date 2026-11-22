def test_dashboard_renders_monitor_section(client):
    response = client.get("/")
    assert b"Monitors" in response.data

def test_dashboard_lists_configured_monitors(client):
    client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"})
    response = client.get("/")
    assert b"Docs" in response.data
    assert b"https://docs.example" in response.data
