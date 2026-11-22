"""Persistence helpers for service monitors."""

from database import connect

def create_monitor(database, name, url, interval_seconds=300):
    connection = connect(database)
    try:
        with connection:
            cursor = connection.execute(
                "INSERT INTO monitors (name, url, interval_seconds) VALUES (?, ?, ?)",
                (name, url, interval_seconds),
            )
            return cursor.lastrowid
    finally:
        connection.close()

def list_monitors(database):
    connection = connect(database)
    try:
        rows = connection.execute(
            "SELECT id, name, url, interval_seconds, enabled, created_at FROM monitors ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def set_monitor_enabled(database, monitor_id, enabled):
    connection = connect(database)
    try:
        with connection:
            cursor = connection.execute(
                "UPDATE monitors SET enabled = ? WHERE id = ?",
                (1 if enabled else 0, monitor_id),
            )
            return cursor.rowcount == 1
    finally:
        connection.close()
