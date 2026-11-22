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


def test_event_lookup_indexes_exist(app):
    connection = connect(app.config["DATABASE"])
    try:
        indexes = {row["name"] for row in connection.execute("PRAGMA index_list(events)")}
        assert {"idx_events_created_at", "idx_events_category", "idx_events_severity"} <= indexes
    finally:
        connection.close()


def test_monitor_schema_is_initialized(app):
    connection = connect(app.config["DATABASE"])
    try:
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(monitors)")}
        assert {"id", "name", "url", "interval_seconds", "enabled", "created_at"} <= columns
    finally:
        connection.close()
