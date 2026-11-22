"""SQLite setup helpers for DevTrack."""

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    details TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT 'note',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def connect(path):
    """Open a SQLite connection with foreign keys enabled."""
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize(path):
    """Create the application schema if it does not exist."""
    with connect(path) as connection:
        connection.executescript(SCHEMA)
