def test_invalid_event_limit_retains_request_id_header(client):
    response = client.get("/api/events?limit=bad", headers={"X-Request-ID": "limit-test"})
    assert response.status_code == 400
    assert response.json["error"] == "limit must be an integer"
    assert response.headers["X-Request-ID"] == "limit-test"
