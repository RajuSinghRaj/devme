def test_csv_export_sets_nosniff_header(client):
    response = client.get("/api/events.csv")
    assert response.headers["X-Content-Type-Options"] == "nosniff"

def test_csv_export_escapes_comma_and_quote_fields(client):
    client.post("/api/events", json={"title": 'A "quoted", title'})
    response = client.get("/api/events.csv")
    assert b'"A ""quoted"", title"' in response.data
