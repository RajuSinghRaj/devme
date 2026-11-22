def test_count_events_cli_command(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=["count-events"])
    assert result.exit_code == 0
    assert result.output.strip() == "0"
