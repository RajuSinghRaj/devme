def test_dashboard_renders_monitor_section(client):
    response = client.get("/")
    assert b"Monitors" in response.data

def test_dashboard_lists_configured_monitors(client):
    client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"})
    response = client.get("/")
    assert b"Docs" in response.data
    assert b"https://docs.example" in response.data


def test_dashboard_shows_monitor_latest_state(client):
    monitor_id = client.post("/api/monitors", json={"name": "Docs", "url": "https://docs.example"}).json["id"]
    client.post(f"/api/monitors/{monitor_id}/results", json={"success": False, "status_code": 503})
    assert b"DOWN" in client.get("/").data


def test_dashboard_displays_next_check_time(client):
    client.post("/api/monitors", json={"name": "Clock", "url": "https://clock.example"})
    response = client.get("/")
    assert b"Next check" in response.data


def test_dashboard_can_create_monitor(client):
    response = client.post("/monitors", data={"name": "Docs", "url": "https://docs.example"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Docs" in response.data

def test_dashboard_ignores_invalid_monitor_url(client):
    response = client.post("/monitors", data={"name": "Bad", "url": "file:///tmp/x"}, follow_redirects=True)
    assert b"Bad" not in response.data


def test_dashboard_monitor_form_is_rendered(client):
    response = client.get("/")
    assert b'id="monitor-name"' in response.data
    assert b'name="url"' in response.data



def test_dashboard_reports_invalid_monitor_form(client):
    response = client.post("/monitors", data={"name": "Bad", "url": "file:///tmp/a"}, follow_redirects=True)
    assert b"valid HTTP or HTTPS URL" in response.data

def test_dashboard_confirms_monitor_creation(client):
    response = client.post("/monitors", data={"name": "Docs", "url": "https://docs.example"}, follow_redirects=True)
    assert b"Monitor saved" in response.data


def test_dashboard_can_pause_and_resume_monitor(client):
    from monitors import list_monitors
    monitor_id = client.post("/api/monitors", json={"name": "Toggle", "url": "https://toggle.example"}).json["id"]
    client.post(f"/monitors/{monitor_id}/toggle")
    assert list_monitors(client.application.config["DATABASE"])[0]["enabled"] == 0
    client.post(f"/monitors/{monitor_id}/toggle")
    assert list_monitors(client.application.config["DATABASE"])[0]["enabled"] == 1

def test_dashboard_can_remove_monitor(client):
    from monitors import list_monitors
    monitor_id = client.post("/api/monitors", json={"name": "Remove", "url": "https://remove.example"}).json["id"]
    assert client.post(f"/monitors/{monitor_id}/delete").status_code == 302
    assert list_monitors(client.application.config["DATABASE"]) == []
