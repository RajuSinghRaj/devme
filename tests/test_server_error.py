def test_unexpected_api_error_returns_generic_json(app, client):
    @app.get("/api/test-failure")
    def fail():
        raise RuntimeError("sensitive internal detail")
    app.config["PROPAGATE_EXCEPTIONS"] = False
    response = client.get("/api/test-failure")
    assert response.status_code == 500
    assert response.json["error"] == "internal server error"
    assert b"sensitive internal detail" not in response.data

def test_unexpected_page_error_returns_generic_html(app, client):
    @app.get("/test-failure")
    def fail_page():
        raise RuntimeError("private detail")
    app.config["PROPAGATE_EXCEPTIONS"] = False
    response = client.get("/test-failure")
    assert response.status_code == 500
    assert b"500 / SERVER ERROR" in response.data
    assert b"private detail" not in response.data
