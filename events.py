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


def get_event(database, event_id):
    """Return one event by identifier, or None when it does not exist."""
    connection = connect(database)
    try:
        row = connection.execute(
            "SELECT id, title, details, category, severity, created_at FROM events WHERE id = ?",
            (event_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def search_events(database, query, limit=50):
    """Find events by title or details using a literal substring."""
    text = str(query).strip()
    if not text:
        return list_events(database, limit)
    bounded_limit = max(1, min(int(limit), 100))
    connection = connect(database)
    try:
        pattern = f"%{text}%"
        rows = connection.execute(
            "SELECT id, title, details, category, severity, created_at FROM events "
            "WHERE title LIKE ? ESCAPE '\\' OR details LIKE ? ESCAPE '\\' ORDER BY id DESC LIMIT ?",
            (pattern, pattern, bounded_limit),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def delete_event(database, event_id):
    """Delete an event and report whether a row was removed."""
    connection = connect(database)
    try:
        with connection:
            cursor = connection.execute("DELETE FROM events WHERE id = ?", (event_id,))
            return cursor.rowcount == 1
    finally:
        connection.close()


def update_event(database, event_id, title, details='', category='note', severity='normal'):
    """Replace editable event fields and report whether it existed."""
    connection = connect(database)
    try:
        with connection:
            cursor = connection.execute(
                "UPDATE events SET title = ?, details = ?, category = ?, severity = ? WHERE id = ?",
                (title, details, category, severity, event_id),
            )
            return cursor.rowcount == 1
    finally:
        connection.close()


def list_categories(database):
    """Return distinct event categories in alphabetical order."""
    connection = connect(database)
    try:
        rows = connection.execute(
            "SELECT DISTINCT category FROM events ORDER BY category COLLATE NOCASE"
        ).fetchall()
        return [row[0] for row in rows]
    finally:
        connection.close()
