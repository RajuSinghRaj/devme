from database import backup, connect
from events import create_event

def test_backup_copies_database_contents(app, tmp_path):
    create_event(app.config["DATABASE"], "Backup entry")
    target = tmp_path / "backup" / "devtrack.sqlite"
    backup(app.config["DATABASE"], target)
    connection = connect(target)
    try:
        assert connection.execute("SELECT title FROM events").fetchone()[0] == "Backup entry"
    finally:
        connection.close()
