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
