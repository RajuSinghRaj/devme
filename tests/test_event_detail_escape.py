def test_event_detail_page_escapes_untrusted_text(client):
    event_id = client.post("/api/events", json={"title": "<img src=x onerror=alert(1)>", "details": "<b>plain text</b>"}).json["id"]
    response = client.get(f"/events/{event_id}")
    assert b"<img src=x" not in response.data
    assert b"&lt;img" in response.data
    assert b"&lt;b&gt;plain text" in response.data
