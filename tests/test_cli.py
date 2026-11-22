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
