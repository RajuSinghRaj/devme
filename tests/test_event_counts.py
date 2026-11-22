from events import count_events

def test_event_count_tracks_inserted_entries(client, app):
    assert count_events(app.config["DATABASE"]) == 0
    client.post("/api/events", json={"title": "One"})
    client.post("/api/events", json={"title": "Two"})
    assert count_events(app.config["DATABASE"]) == 2
