"""SQLite setup helpers for DevTrack."""

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    details TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT 'note',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    severity TEXT NOT NULL DEFAULT 'normal' CHECK (severity IN ('low', 'normal', 'high'))
 );
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_category ON events (category);
CREATE INDEX IF NOT EXISTS idx_events_severity ON events (severity);
CREATE TABLE IF NOT EXISTS monitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    interval_seconds INTEGER NOT NULL DEFAULT 300 CHECK (interval_seconds >= 30),
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
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
    connection = connect(path)
    try:
        with connection:
            connection.executescript(SCHEMA)
    finally:
        connection.close()
