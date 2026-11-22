from monitors import create_monitor, list_monitors

def test_monitor_can_be_saved_and_listed(app):
    monitor_id = create_monitor(app.config["DATABASE"], "Docs", "https://docs.example")
    monitors = list_monitors(app.config["DATABASE"])
    assert monitors[0]["id"] == monitor_id
    assert monitors[0]["url"] == "https://docs.example"
    assert monitors[0]["enabled"] == 1
