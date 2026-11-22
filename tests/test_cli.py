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
