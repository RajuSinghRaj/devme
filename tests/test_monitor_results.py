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


def test_monitor_results_are_listed_newest_first(app):
    from monitors import list_results
    monitor_id = create_monitor(app.config["DATABASE"], "Docs", "https://docs.example")
    record_result(app.config["DATABASE"], monitor_id, True, 200, 20)
    record_result(app.config["DATABASE"], monitor_id, False, 503, 80, "unavailable")
    results = list_results(app.config["DATABASE"], monitor_id)
    assert len(results) == 2
    assert results[0]["success"] == 0
    assert results[0]["error"] == "unavailable"


def test_monitor_summary_calculates_success_rate(app):
    from monitors import monitor_summary
    monitor_id = create_monitor(app.config["DATABASE"], "Docs", "https://docs.example")
    assert monitor_summary(app.config["DATABASE"], monitor_id)["uptime_percent"] is None
    record_result(app.config["DATABASE"], monitor_id, True, 200, 20)
    record_result(app.config["DATABASE"], monitor_id, False, 503, 80)
    summary = monitor_summary(app.config["DATABASE"], monitor_id)
    assert summary["total_checks"] == 2
    assert summary["uptime_percent"] == 50.0
    assert summary["latest"]["success"] == 0


def test_old_monitor_results_can_be_pruned(app):
    from monitors import list_results, prune_results
    monitor_id = create_monitor(app.config["DATABASE"], "Docs", "https://docs.example")
    record_result(app.config["DATABASE"], monitor_id, True, 200, 10)
    removed = prune_results(app.config["DATABASE"], "2999-01-01 00:00:00")
    assert removed == 1
    assert list_results(app.config["DATABASE"], monitor_id) == []



def test_monitor_summary_counts_current_failure_streak(app):
    from monitors import monitor_summary
    monitor_id = create_monitor(app.config["DATABASE"], "Docs", "https://docs.example")
    record_result(app.config["DATABASE"], monitor_id, True, 200, 10)
    record_result(app.config["DATABASE"], monitor_id, False, 503, 20)
    record_result(app.config["DATABASE"], monitor_id, False, 503, 25)
    assert monitor_summary(app.config["DATABASE"], monitor_id)["failure_streak"] == 2
