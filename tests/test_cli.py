def test_count_events_cli_command(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=["count-events"])
    assert result.exit_code == 0
    assert result.output.strip() == "0"


def test_init_database_cli_command(app):
    result = app.test_cli_runner().invoke(args=["init-db"])
    assert result.exit_code == 0
    assert "Database ready" in result.output


def test_count_monitors_cli_command(app):
    result = app.test_cli_runner().invoke(args=["count-monitors"])
    assert result.exit_code == 0
    assert result.output.strip() == "0"


def test_export_events_cli_writes_csv(app, tmp_path):
    from events import create_event
    create_event(app.config["DATABASE"], "CLI export")
    target = tmp_path / "exports" / "events.csv"
    result = app.test_cli_runner().invoke(args=["export-events", "--output", str(target)])
    assert result.exit_code == 0
    assert "CLI export" in target.read_text(encoding="utf-8")


def test_backup_database_cli_command(app, tmp_path):
    target = tmp_path / "copies" / "backup.sqlite"
    result = app.test_cli_runner().invoke(args=["backup-db", "--output", str(target)])
    assert result.exit_code == 0
    assert target.exists()


def test_prune_checks_cli_command(app):
    result = app.test_cli_runner().invoke(args=["prune-checks", "--before", "2999-01-01 00:00:00"])
    assert result.exit_code == 0
    assert "Removed 0" in result.output


def test_export_events_cli_can_write_to_stdout(app):
    from events import create_event
    create_event(app.config["DATABASE"], "Stdout export")
    result = app.test_cli_runner().invoke(args=["export-events"])
    assert result.exit_code == 0
    assert "Stdout export" in result.output


def test_check_monitor_cli_reports_mocked_result(app, monkeypatch):
    import app as app_module
    monkeypatch.setattr(app_module, "check_monitor", lambda database, monitor_id: {"success": True, "status_code": 200, "response_ms": 12.5})
    result = app.test_cli_runner().invoke(args=["check-monitor", "1"])
    assert result.exit_code == 0
    assert "UP status=200 duration_ms=12.5" in result.output


def test_check_due_cli_reports_no_due_monitors(app):
    result = app.test_cli_runner().invoke(args=["check-due"])
    assert result.exit_code == 0
    assert "Checked 0 monitor(s)" in result.output


def test_prune_events_cli_command(app):
    result = app.test_cli_runner().invoke(args=["prune-events", "--before", "2999-01-01 00:00:00"])
    assert result.exit_code == 0
    assert "Removed 0 event(s)" in result.output
