from database import connect, initialize

def test_app_fixture_initializes_event_schema(app):
    connection = connect(app.config["DATABASE"])
    try:
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(events)")}
        assert {"id", "title", "details", "category", "severity", "created_at"} <= columns
    finally:
        connection.close()

def test_database_rejects_unknown_severity(app):
    connection = connect(app.config["DATABASE"])
    try:
        try:
            connection.execute("INSERT INTO events (title, severity) VALUES (?, ?)", ("bad", "urgent"))
        except Exception:
            pass
        else:
            raise AssertionError("invalid severity was accepted")
    finally:
        connection.close()
