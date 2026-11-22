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
            "SELECT m.id, m.name, m.url, m.interval_seconds, m.enabled, m.created_at, "
            "(SELECT success FROM monitor_results r WHERE r.monitor_id = m.id ORDER BY r.id DESC LIMIT 1) AS last_success, "
            "(SELECT checked_at FROM monitor_results r WHERE r.monitor_id = m.id ORDER BY r.id DESC LIMIT 1) AS last_checked, "
            "datetime(COALESCE((SELECT checked_at FROM monitor_results r WHERE r.monitor_id = m.id ORDER BY r.id DESC LIMIT 1), m.created_at), '+' || m.interval_seconds || ' seconds') AS next_check_at, "
            "(m.enabled = 1 AND datetime('now') >= datetime(COALESCE((SELECT checked_at FROM monitor_results r WHERE r.monitor_id = m.id ORDER BY r.id DESC LIMIT 1), m.created_at), '+' || m.interval_seconds || ' seconds')) AS is_due "
            "FROM monitors m ORDER BY m.id DESC"
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


def delete_monitor(database, monitor_id):
    connection = connect(database)
    try:
        with connection:
            cursor = connection.execute("DELETE FROM monitors WHERE id = ?", (monitor_id,))
            return cursor.rowcount == 1
    finally:
        connection.close()


def record_result(database, monitor_id, success, status_code=None, response_ms=None, error=''):
    connection = connect(database)
    try:
        with connection:
            cursor = connection.execute(
                "INSERT INTO monitor_results (monitor_id, success, status_code, response_ms, error) "
                "VALUES (?, ?, ?, ?, ?)",
                (monitor_id, int(bool(success)), status_code, response_ms, error[:500]),
            )
            return cursor.lastrowid
    finally:
        connection.close()


def list_results(database, monitor_id, limit=50):
    bounded_limit = max(1, min(int(limit), 100))
    connection = connect(database)
    try:
        rows = connection.execute(
            "SELECT id, monitor_id, success, status_code, response_ms, checked_at, error "
            "FROM monitor_results WHERE monitor_id = ? ORDER BY id DESC LIMIT ?",
            (monitor_id, bounded_limit),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def monitor_summary(database, monitor_id):
    connection = connect(database)
    try:
        row = connection.execute(
            "SELECT COUNT(*) AS total, COALESCE(SUM(success), 0) AS successes "
            "FROM monitor_results WHERE monitor_id = ?",
            (monitor_id,),
        ).fetchone()
        latest = connection.execute(
            "SELECT success, status_code, response_ms, checked_at, error "
            "FROM monitor_results WHERE monitor_id = ? ORDER BY id DESC LIMIT 1",
            (monitor_id,),
        ).fetchone()
        recent = connection.execute(
            "SELECT success FROM monitor_results WHERE monitor_id = ? ORDER BY id DESC LIMIT 100",
            (monitor_id,),
        ).fetchall()
        failure_streak = 0
        for result in recent:
            if result["success"]:
                break
            failure_streak += 1
        total = row["total"]
        return {
            "total_checks": total,
            "successful_checks": row["successes"],
            "uptime_percent": round(row["successes"] * 100 / total, 2) if total else None,
            "latest": dict(latest) if latest else None,
            "failure_streak": failure_streak,
        }
    finally:
        connection.close()


def get_monitor(database, monitor_id):
    return next((item for item in list_monitors(database) if item["id"] == monitor_id), None)


def update_monitor(database, monitor_id, name, url, interval_seconds):
    connection = connect(database)
    try:
        with connection:
            cursor = connection.execute(
                "UPDATE monitors SET name = ?, url = ?, interval_seconds = ? WHERE id = ?",
                (name, url, interval_seconds, monitor_id),
            )
            return cursor.rowcount == 1
    finally:
        connection.close()


def prune_results(database, before):
    """Delete check history older than an ISO-8601 cutoff timestamp."""
    connection = connect(database)
    try:
        with connection:
            cursor = connection.execute("DELETE FROM monitor_results WHERE checked_at < ?", (before,))
            return cursor.rowcount
    finally:
        connection.close()
