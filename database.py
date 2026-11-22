"""SQLite setup helpers for DevTrack."""

import sqlite3
from pathlib import Path

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
CREATE TABLE IF NOT EXISTS monitor_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_id INTEGER NOT NULL REFERENCES monitors(id) ON DELETE CASCADE,
    success INTEGER NOT NULL CHECK (success IN (0, 1)),
    status_code INTEGER,
    response_ms REAL CHECK (response_ms IS NULL OR response_ms >= 0),
    checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    error TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_results_monitor_checked ON monitor_results (monitor_id, checked_at DESC);
"""

def connect(path):
    """Open a SQLite connection with foreign keys enabled."""
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize(path):
    """Create parent folders and initialize the application schema."""
    database_path = Path(path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = connect(str(database_path))
    try:
        with connection:
            connection.executescript(SCHEMA)
    finally:
        connection.close()


def backup(source, destination):
    """Create a consistent SQLite backup at destination."""
    destination_path = Path(destination)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    source_connection = connect(source)
    target_connection = sqlite3.connect(str(destination_path))
    try:
        source_connection.backup(target_connection)
    finally:
        target_connection.close()
        source_connection.close()
