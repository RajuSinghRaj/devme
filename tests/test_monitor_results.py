from monitors import create_monitor, record_result
from database import connect

def test_monitor_result_can_be_recorded(app):
    monitor_id = create_monitor(app.config["DATABASE"], "Docs", "https://docs.example")
    result_id = record_result(app.config["DATABASE"], monitor_id, True, 200, 42.5)
    connection = connect(app.config["DATABASE"])
    try:
        row = connection.execute("SELECT * FROM monitor_results WHERE id = ?", (result_id,)).fetchone()
        assert row["success"] == 1
        assert row["status_code"] == 200
        assert row["response_ms"] == 42.5
    finally:
        connection.close()
