def test_csv_export_uses_utf8_content_type(client):
    response = client.get("/api/events.csv")
    assert response.mimetype == "text/csv"
    assert response.mimetype_params["charset"] == "utf-8"
