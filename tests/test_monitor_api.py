def test_monitor_api_lists_empty_collection(client):
    response = client.get("/api/monitors")
    assert response.status_code == 200
    assert response.json == {"monitors": []}


def test_monitor_api_creates_valid_monitor(client):
    response = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"})
    assert response.status_code == 201
    assert client.get("/api/monitors").json["monitors"][0]["name"] == "Docs"

def test_monitor_api_rejects_non_http_url(client):
    response = client.post("/api/monitors", json={"name": "Bad", "url": "file:///etc/passwd"})
    assert response.status_code == 400
