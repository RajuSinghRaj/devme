def test_response_contains_generated_request_id(client):
    response = client.get("/health")
    assert len(response.headers["X-Request-ID"]) == 32

def test_request_id_can_be_provided_by_caller(client):
    response = client.get("/health", headers={"X-Request-ID": "trace-123"})
    assert response.headers["X-Request-ID"] == "trace-123"


def test_request_completion_is_logged(client, caplog):
    with caplog.at_level("INFO"):
        client.get("/health", headers={"X-Request-ID": "trace-log"})
    assert any(record.request_id == "trace-log" for record in caplog.records)


def test_invalid_request_id_is_replaced(client):
    response = client.get("/health", headers={"X-Request-ID": "bad id"})
    assert response.headers["X-Request-ID"] != "bad id"
    assert len(response.headers["X-Request-ID"]) == 32

def test_oversized_request_id_is_replaced(client):
    response = client.get("/health", headers={"X-Request-ID": "x" * 100})
    assert len(response.headers["X-Request-ID"]) == 32
