def test_dashboard_renders_branding(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"DEVTRACK" in response.data

def test_dashboard_has_entry_form(client):
    response = client.get("/")
    assert b'name="title"' in response.data
    assert b'name="details"' in response.data


def test_dashboard_event_titles_link_to_details(client):
    event_id = client.post("/api/events", json={"title": "Linked entry"}).json["id"]
    response = client.get("/")
    assert f'/events/{event_id}'.encode() in response.data
