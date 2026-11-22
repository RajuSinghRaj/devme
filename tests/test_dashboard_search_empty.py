def test_dashboard_search_with_no_matches_shows_empty_state(client):
    response = client.get("/?q=no-such-entry")
    assert response.status_code == 200
    assert b"Your log starts here" in response.data
    assert b"no-such-entry" in response.data
