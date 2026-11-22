def test_dashboard_renders_branding(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"DEVTRACK" in response.data

def test_dashboard_has_entry_form(client):
    response = client.get("/")
    assert b'name="title"' in response.data
    assert b'name="details"' in response.data
