def test_csv_export_includes_event_and_download_headers(client):
    client.post("/api/events", json={"title": "CSV entry"})
    response = client.get("/api/events.csv")
    assert response.status_code == 200
    assert "text/csv" in response.content_type
    assert "attachment" in response.headers["Content-Disposition"]
    assert b"CSV entry" in response.data

def test_csv_export_neutralizes_formula_cells(client):
    client.post("/api/events", json={"title": "=1+1"})
    assert b"'=1+1" in client.get("/api/events.csv").data


def test_csv_export_has_stable_header_when_empty(client):
    response = client.get("/api/events.csv")
    assert response.data.splitlines()[0] == b"id,title,details,category,severity,created_at"
