def test_monitor_detail_escapes_url_and_name(client):
    monitor_id = client.post("/api/monitors", json={"name": "<b>Status</b>", "url": "https://status.example/?x=1&y=2"}).json["id"]
    response = client.get(f"/monitors/{monitor_id}")
    assert b"&lt;b&gt;Status" in response.data
    assert b"x=1&amp;y=2" in response.data
