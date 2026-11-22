def test_monitor_api_lists_empty_collection(client):
    response = client.get("/api/monitors")
    assert response.status_code == 200
    assert response.json == {"monitors": []}
