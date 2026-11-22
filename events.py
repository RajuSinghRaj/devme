import csv
import io

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


def list_events(database, limit=50, offset=0):
    """Return newest events first, bounded to a safe page size."""
    bounded_limit = max(1, min(int(limit), 100))
    bounded_offset = max(0, int(offset))
    connection = connect(database)
    try:
        rows = connection.execute(
            "SELECT id, title, details, category, severity, created_at FROM events ORDER BY id DESC LIMIT ? OFFSET ?",
            (bounded_limit, bounded_offset),
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


def count_events(database):
    """Return the number of stored activity entries."""
    connection = connect(database)
    try:
        return connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    finally:
        connection.close()


def list_events_by_category(database, category, limit=50):
    """List newest events from one category."""
    bounded_limit = max(1, min(int(limit), 100))
    connection = connect(database)
    try:
        rows = connection.execute(
            "SELECT id, title, details, category, severity, created_at FROM events "
            "WHERE category = ? ORDER BY id DESC LIMIT ?",
            (category, bounded_limit),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def latest_event(database):
    """Return the most recently created event, when one exists."""
    connection = connect(database)
    try:
        row = connection.execute(
            "SELECT id, title, details, category, severity, created_at FROM events ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def export_events_csv(database):
    """Serialize stored activity entries as a UTF-8 CSV document."""
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(("id", "title", "details", "category", "severity", "created_at"))
    for event in list_events(database, 100):
        values = []
        for key in ("id", "title", "details", "category", "severity", "created_at"):
            value = event[key]
            if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")):
                value = "'" + value
            values.append(value)
        writer.writerow(values)
    return output.getvalue()
