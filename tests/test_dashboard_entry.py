def test_dashboard_entry_persists_category_and_severity(client):
    client.post("/events", data={
        "title": "Deploy release",
        "category": "build",
        "severity": "high",
    })
    response = client.get("/")
    assert b"Deploy release" in response.data
    assert b"BUILD" in response.data
    assert b"HIGH" in response.data

def test_dashboard_rejects_blank_entry_title(client):
    response = client.post("/events", data={"title": ""}, follow_redirects=True)
    assert b"Add a title before saving" in response.data


def test_entry_form_includes_existing_custom_categories(client):
    client.post("/api/events", json={"title": "Document", "category": "release"})
    assert b'value="release"' in client.get("/").data


def test_new_category_options_are_sorted_case_insensitively(client):
    client.post("/api/events", json={"title": "One", "category": "Alpha"})
    client.post("/api/events", json={"title": "Two", "category": "zeta"})
    html = client.get("/").data
    assert html.index(b'value="Alpha"') < html.index(b'value="zeta"')
