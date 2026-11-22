from monitors import create_monitor, list_monitors

def test_monitor_can_be_saved_and_listed(app):
    monitor_id = create_monitor(app.config["DATABASE"], "Docs", "https://docs.example")
    monitors = list_monitors(app.config["DATABASE"])
    assert monitors[0]["id"] == monitor_id
    assert monitors[0]["url"] == "https://docs.example"
    assert monitors[0]["enabled"] == 1


def test_monitor_can_be_paused_and_resumed(app):
    monitor_id = create_monitor(app.config["DATABASE"], "Docs", "https://docs.example")
    from monitors import set_monitor_enabled
    assert set_monitor_enabled(app.config["DATABASE"], monitor_id, False)
    assert list_monitors(app.config["DATABASE"])[0]["enabled"] == 0
    assert set_monitor_enabled(app.config["DATABASE"], monitor_id, True)
    assert list_monitors(app.config["DATABASE"])[0]["enabled"] == 1


def test_monitor_can_be_deleted(app):
    from monitors import delete_monitor
    monitor_id = create_monitor(app.config["DATABASE"], "Docs", "https://docs.example")
    assert delete_monitor(app.config["DATABASE"], monitor_id)
    assert list_monitors(app.config["DATABASE"]) == []


def test_monitor_listing_includes_latest_check_state(app):
    from monitors import record_result
    monitor_id = create_monitor(app.config["DATABASE"], "Docs", "https://docs.example")
    record_result(app.config["DATABASE"], monitor_id, False, 503, 90, "down")
    monitor = list_monitors(app.config["DATABASE"])[0]
    assert monitor["last_success"] == 0
    assert monitor["last_checked"] is not None


def test_monitor_names_and_urls_are_returned_as_saved(app):
    name = "Build & Release"
    url = "https://example.com/status?region=west"
    create_monitor(app.config["DATABASE"], name, url)
    monitor = list_monitors(app.config["DATABASE"])[0]
    assert monitor["name"] == name
    assert monitor["url"] == url


def test_monitor_can_be_retrieved_by_id(app):
    from monitors import get_monitor
    monitor_id = create_monitor(app.config["DATABASE"], "Docs", "https://docs.example")
    assert get_monitor(app.config["DATABASE"], monitor_id)["name"] == "Docs"
    assert get_monitor(app.config["DATABASE"], 999) is None


def test_monitor_metadata_can_be_updated(app):
    from monitors import get_monitor, update_monitor
    monitor_id = create_monitor(app.config["DATABASE"], "Docs", "https://docs.example")
    assert update_monitor(app.config["DATABASE"], monitor_id, "Status", "https://status.example", 600)
    monitor = get_monitor(app.config["DATABASE"], monitor_id)
    assert monitor["name"] == "Status"
    assert monitor["url"] == "https://status.example"
    assert monitor["interval_seconds"] == 600
