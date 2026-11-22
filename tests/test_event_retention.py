from events import create_event, list_events, prune_events

def test_event_retention_removes_rows_before_cutoff(app):
    create_event(app.config["DATABASE"], "Old row")
    removed = prune_events(app.config["DATABASE"], "2999-01-01 00:00:00")
    assert removed == 1
    assert list_events(app.config["DATABASE"]) == []

def test_event_retention_keeps_rows_after_cutoff(app):
    create_event(app.config["DATABASE"], "Recent row")
    assert prune_events(app.config["DATABASE"], "2000-01-01 00:00:00") == 0
    assert list_events(app.config["DATABASE"])[0]["title"] == "Recent row"
