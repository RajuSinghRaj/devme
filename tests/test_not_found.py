def test_unknown_api_route_returns_json_error(client):
    response = client.get("/api/unknown")
    assert response.status_code == 404
    assert response.json["error"] == "not found"
    assert response.json["request_id"] == response.headers["X-Request-ID"]

def test_unknown_page_renders_custom_error(client):
    response = client.get("/missing-page")
    assert response.status_code == 404
    assert b"404 / NOT FOUND" in response.data
