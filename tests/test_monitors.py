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
