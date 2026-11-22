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


def test_check_runner_blocks_private_network_targets(app):
    monitor_id = create_monitor(app.config["DATABASE"], "Private", "http://127.0.0.1")
    called = []
    def fetcher(url, timeout):
        called.append(url)
        return FakeResponse(200)
    result = check_monitor(app.config["DATABASE"], monitor_id, fetcher, lambda host, port: [(None, None, None, None, ("127.0.0.1", 0))])
    assert result["success"] is False
    assert "non-public" in result["error"]
    assert called == []

def test_check_runner_skips_paused_monitors(app):
    from monitors import set_monitor_enabled
    monitor_id = create_monitor(app.config["DATABASE"], "Paused", "https://example.com")
    set_monitor_enabled(app.config["DATABASE"], monitor_id, False)
    try:
        check_monitor(app.config["DATABASE"], monitor_id, lambda *_: FakeResponse(200), public_resolver)
    except ValueError as error:
        assert "paused" in str(error)
    else:
        raise AssertionError("paused monitor was executed")
