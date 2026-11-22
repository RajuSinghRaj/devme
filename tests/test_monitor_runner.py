from monitors import check_monitor, create_monitor, list_results

class FakeResponse:
    def __init__(self, status):
        self.status = status
        self.closed = False
    def getcode(self):
        return self.status
    def close(self):
        self.closed = True

def public_resolver(host, port):
    return [(None, None, None, None, ("93.184.216.34", 0))]

def test_check_runner_records_success(app):
    monitor_id = create_monitor(app.config["DATABASE"], "Site", "https://example.com")
    result = check_monitor(app.config["DATABASE"], monitor_id, lambda url, timeout: FakeResponse(200), public_resolver)
    assert result["success"] is True
    assert result["status_code"] == 200
    assert result["response_ms"] >= 0
    assert len(list_results(app.config["DATABASE"], monitor_id)) == 1

def test_check_runner_records_unexpected_status(app):
    monitor_id = create_monitor(app.config["DATABASE"], "Site", "https://example.com")
    result = check_monitor(app.config["DATABASE"], monitor_id, lambda url, timeout: FakeResponse(503), public_resolver)
    assert result["success"] is False
    assert result["error"] == "unexpected HTTP status 503"
