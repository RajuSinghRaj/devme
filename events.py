"""Persistence helpers for developer activity entries."""

from database import connect

def create_event(database, title, details='', category='note', severity='normal'):
    """Store one event and return its generated identifier."""
    connection = connect(database)
    try:
        with connection:
            cursor = connection.execute(
                "INSERT INTO events (title, details, category, severity) VALUES (?, ?, ?, ?)",
                (title, details, category, severity),
            )
            return cursor.lastrowid
    finally:
        connection.close()


def list_events(database, limit=50):
    """Return newest events first, bounded to a safe page size."""
    bounded_limit = max(1, min(int(limit), 100))
    connection = connect(database)
    try:
        rows = connection.execute(
            "SELECT id, title, details, category, severity, created_at FROM events ORDER BY id DESC LIMIT ?",
            (bounded_limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()
