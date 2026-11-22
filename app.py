from datetime import datetime, timezone
import os
import re
import time
import uuid
from urllib.parse import urlsplit
from pathlib import Path

from database import backup, initialize
from monitors import create_monitor, delete_monitor, get_monitor, list_monitors, list_results, monitor_summary, prune_results, record_result, update_monitor, set_monitor_enabled
from events import create_event, delete_event, event_breakdown, filter_events, count_events, export_events_csv, latest_event, list_categories, list_events, list_events_by_category, list_events_by_severity, search_events, update_event

from flask import Flask, g, jsonify, make_response, redirect, render_template, request, url_for
import click


def create_app(test_config=None):
    """Create and configure the DevTrack Flask application."""
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("DEVTRACK_SECRET_KEY", "devtrack-local-key"),
        TESTING=False,
        LOG_LEVEL=os.environ.get("DEVTRACK_LOG_LEVEL", "INFO").upper(),
        DATABASE=os.environ.get("DEVTRACK_DATABASE", str(Path(app.instance_path) / "devtrack.sqlite")),
    )
    if test_config:
        app.config.update(test_config)
    import logging
    app.logger.setLevel(getattr(logging, app.config["LOG_LEVEL"], logging.INFO))
    initialize(app.config["DATABASE"])

    @app.before_request
    def assign_request_id():
        supplied_id = request.headers.get("X-Request-ID", "")
        g.request_id = supplied_id if re.fullmatch(r"[A-Za-z0-9._-]{1,64}", supplied_id) else uuid.uuid4().hex

    @app.after_request
    def add_content_type_options(response):
        response.headers["X-Request-ID"] = g.request_id
        app.logger.info("request complete", extra={"request_id": g.request_id, "http_status": response.status_code})
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    @app.context_processor
    def inject_now():
        now = datetime.now(timezone.utc)
        return {"current_year": now.year, "today_label": f"{now:%A, %B} {now.day}"}

    app.extensions["devtrack_started_at"] = time.monotonic()

    @app.cli.command("prune-checks")
    @click.option("--before", required=True, help="ISO timestamp cutoff, for example 2025-01-01 00:00:00.")
    def prune_checks_command(before):
        """Remove monitor check history older than a cutoff."""
        removed = prune_results(app.config["DATABASE"], before)
        click.echo(f"Removed {removed} monitor results")

    @app.cli.command("backup-db")
    @click.option("--output", required=True, type=click.Path(path_type=Path))
    def backup_database_command(output):
        """Write a consistent backup of the configured SQLite database."""
        backup(app.config["DATABASE"], output)
        click.echo(f"Database backup written to {output}")

    @app.cli.command("init-db")
    def initialize_database_command():
        """Initialize the configured DevTrack database."""
        initialize(app.config["DATABASE"])
        click.echo("Database ready")

    @app.cli.command("export-events")
    @click.option("--output", type=click.Path(path_type=Path), help="Write CSV to this path instead of stdout.")
    def export_events_command(output):
        """Export log entries as CSV."""
        csv_text = export_events_csv(app.config["DATABASE"])
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(csv_text, encoding="utf-8", newline="")
            click.echo(f"Exported events to {output}")
        else:
            click.echo(csv_text, nl=False)

    @app.cli.command("count-monitors")
    def count_monitors_command():
        """Print the number of configured monitors."""
        click.echo(len(list_monitors(app.config["DATABASE"])))

    @app.cli.command("count-events")
    def count_events_command():
        """Print the number of saved developer log entries."""
        click.echo(count_events(app.config["DATABASE"]))

    @app.errorhandler(404)
    def handle_not_found(error):
        if request.path.startswith("/api/"):
            return jsonify(error="not found", request_id=g.request_id), 404
        return render_template("404.html"), 404

    @app.get("/health")
    def health():
        return jsonify(status="ok", service="DevTrack")

    @app.post("/api/events")
    def api_create_event():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="JSON object required"), 400
        title = payload.get("title", "")
        if not isinstance(title, str) or not title.strip():
            return jsonify(error="title is required"), 400
        severity = payload.get("severity", "normal")
        if not isinstance(severity, str) or severity not in {"low", "normal", "high"}:
            return jsonify(error="severity must be low, normal, or high"), 400
        event_id = create_event(
            app.config["DATABASE"], title.strip()[:120],
            payload.get("details", "")[:2000] if isinstance(payload.get("details", ""), str) else "",
            payload.get("category", "note")[:40] if isinstance(payload.get("category", "note"), str) else "note",
            severity,
        )
        response = jsonify(id=event_id)
        response.headers["Location"] = url_for("api_event_detail", event_id=event_id)
        return response, 201

    @app.put("/api/events/<int:event_id>")
    def api_update_event(event_id):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="JSON object required"), 400
        title = payload.get("title")
        severity = payload.get("severity", "normal")
        if not isinstance(title, str) or not title.strip():
            return jsonify(error="title is required"), 400
        if not isinstance(severity, str) or severity not in {"low", "normal", "high"}:
            return jsonify(error="invalid severity"), 400
        updated = update_event(
            app.config["DATABASE"], event_id, title.strip()[:120],
            payload.get("details", "")[:2000] if isinstance(payload.get("details", ""), str) else "",
            payload.get("category", "note")[:40] if isinstance(payload.get("category", "note"), str) else "note", severity,
        )
        if not updated:
            return jsonify(error="event not found"), 404
        return jsonify(id=event_id, updated=True)

    @app.delete("/api/events/<int:event_id>")
    def api_delete_event(event_id):
        if not delete_event(app.config["DATABASE"], event_id):
            return jsonify(error="event not found"), 404
        return "", 204

    @app.get("/api/events/<int:event_id>")
    def api_event_detail(event_id):
        from events import get_event
        event = get_event(app.config["DATABASE"], event_id)
        if event is None:
            return jsonify(error="event not found"), 404
        return jsonify(event=event)

    @app.get("/api/events.csv")
    def api_export_events():
        response = make_response(export_events_csv(app.config["DATABASE"]))
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        response.headers["Content-Disposition"] = "attachment; filename=devtrack-events.csv"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.get("/api/events/breakdown")
    def api_event_breakdown():
        return jsonify(event_breakdown(app.config["DATABASE"]))

    @app.get("/api/summary")
    def api_summary():
        return jsonify(event_count=count_events(app.config["DATABASE"]), category_count=len(list_categories(app.config["DATABASE"])), monitor_count=len(list_monitors(app.config["DATABASE"])), latest_event=latest_event(app.config["DATABASE"]))

    @app.get("/monitors/<int:monitor_id>")
    def monitor_detail(monitor_id):
        monitor = next((row for row in list_monitors(app.config["DATABASE"]) if row["id"] == monitor_id), None)
        if monitor is None:
            return render_template("404.html"), 404
        return render_template("monitor.html", monitor=monitor, results=list_results(app.config["DATABASE"], monitor_id))

    @app.get("/api/monitors/<int:monitor_id>/schedule")
    def api_monitor_schedule(monitor_id):
        monitor = get_monitor(app.config["DATABASE"], monitor_id)
        if monitor is None:
            return jsonify(error="monitor not found"), 404
        return jsonify(is_due=bool(monitor["is_due"]), next_check_at=monitor["next_check_at"], interval_seconds=monitor["interval_seconds"])

    @app.get("/api/monitors/<int:monitor_id>/summary")
    def api_monitor_summary(monitor_id):
        if not any(row["id"] == monitor_id for row in list_monitors(app.config["DATABASE"])):
            return jsonify(error="monitor not found"), 404
        return jsonify(summary=monitor_summary(app.config["DATABASE"], monitor_id))

    @app.get("/api/monitors/<int:monitor_id>/results")
    def api_monitor_results(monitor_id):
        known = any(row["id"] == monitor_id for row in list_monitors(app.config["DATABASE"]))
        if not known:
            return jsonify(error="monitor not found"), 404
        return jsonify(results=list_results(app.config["DATABASE"], monitor_id))

    @app.post("/api/monitors/<int:monitor_id>/results")
    def api_record_monitor_result(monitor_id):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or not isinstance(payload.get("success"), bool):
            return jsonify(error="success boolean is required"), 400
        known = any(row["id"] == monitor_id for row in list_monitors(app.config["DATABASE"]))
        if not known:
            return jsonify(error="monitor not found"), 404
        status_code = payload.get("status_code")
        response_ms = payload.get("response_ms")
        if status_code is not None and (not isinstance(status_code, int) or not 100 <= status_code <= 599):
            return jsonify(error="status_code must be between 100 and 599"), 400
        if response_ms is not None and (not isinstance(response_ms, (int, float)) or response_ms < 0):
            return jsonify(error="response_ms must be nonnegative"), 400
        result_id = record_result(app.config["DATABASE"], monitor_id, payload["success"], status_code, response_ms, str(payload.get("error", "")))
        return jsonify(id=result_id), 201

    @app.put("/api/monitors/<int:monitor_id>")
    def api_replace_monitor(monitor_id):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="JSON object required"), 400
        name, url = payload.get("name"), payload.get("url")
        try:
            interval = int(payload.get("interval_seconds", 300))
        except (TypeError, ValueError):
            return jsonify(error="interval_seconds must be an integer"), 400
        if not isinstance(name, str) or not name.strip():
            return jsonify(error="name is required"), 400
        parsed_url = urlsplit(url) if isinstance(url, str) else None
        if not parsed_url or parsed_url.scheme not in {"http", "https"} or not parsed_url.hostname or parsed_url.username or parsed_url.password:
            return jsonify(error="url must be an absolute HTTP or HTTPS URL without credentials"), 400
        if interval < 30:
            return jsonify(error="interval_seconds must be at least 30"), 400
        if not update_monitor(app.config["DATABASE"], monitor_id, name.strip()[:120], url[:2048], interval):
            return jsonify(error="monitor not found"), 404
        return jsonify(monitor=get_monitor(app.config["DATABASE"], monitor_id))

    @app.patch("/api/monitors/<int:monitor_id>")
    def api_update_monitor(monitor_id):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or not isinstance(payload.get("enabled"), bool):
            return jsonify(error="enabled boolean is required"), 400
        if not set_monitor_enabled(app.config["DATABASE"], monitor_id, payload["enabled"]):
            return jsonify(error="monitor not found"), 404
        return jsonify(id=monitor_id, enabled=payload["enabled"])

    @app.delete("/api/monitors/<int:monitor_id>")
    def api_delete_monitor(monitor_id):
        if not delete_monitor(app.config["DATABASE"], monitor_id):
            return jsonify(error="monitor not found"), 404
        return "", 204

    @app.post("/api/monitors")
    def api_create_monitor():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="JSON object required"), 400
        name = payload.get("name", "")
        url = payload.get("url", "")
        interval = payload.get("interval_seconds", 300)
        if not isinstance(name, str) or not name.strip():
            return jsonify(error="name is required"), 400
        parsed_url = urlsplit(url) if isinstance(url, str) else None
        if not parsed_url or parsed_url.scheme not in {"http", "https"} or not parsed_url.hostname or parsed_url.username or parsed_url.password:
            return jsonify(error="url must be an absolute HTTP or HTTPS URL without credentials"), 400
        try:
            interval = int(interval)
        except (TypeError, ValueError):
            return jsonify(error="interval_seconds must be an integer"), 400
        if interval < 30:
            return jsonify(error="interval_seconds must be at least 30"), 400
        monitor_id = create_monitor(app.config["DATABASE"], name.strip()[:120], url[:2048], interval)
        return jsonify(id=monitor_id), 201

    @app.get("/api/monitors/<int:monitor_id>")
    def api_monitor_detail(monitor_id):
        monitor = get_monitor(app.config["DATABASE"], monitor_id)
        if monitor is None:
            return jsonify(error="monitor not found"), 404
        return jsonify(monitor=monitor)

    @app.get("/api/monitors")
    def api_monitors():
        return jsonify(monitors=list_monitors(app.config["DATABASE"]))

    @app.get("/api/categories")
    def api_categories():
        return jsonify(categories=list_categories(app.config["DATABASE"]))

    @app.get("/api/events")
    def api_events():
        try:
            limit = int(request.args.get("limit", "50"))
            page = int(request.args.get("page", "1"))
            if page < 1:
                raise ValueError
        except ValueError:
            return jsonify(error="limit must be an integer"), 400
        query = request.args.get("q", "")[:100]
        category = request.args.get("category", "")[:40]
        severity = request.args.get("severity", "")[:10]
        page_size = min(max(limit, 1), 100)
        entries = filter_events(app.config["DATABASE"], query, category, severity, page_size, (page - 1) * page_size)
        return jsonify(events=entries, page=page, limit=min(max(limit, 1), 100))

    @app.get("/version")
    def version():
        return jsonify(name="DevTrack", version="0.1.0")

    @app.get("/health/live")
    def liveness():
        return jsonify(status="alive")

    @app.get("/health/uptime")
    def uptime():
        elapsed = time.monotonic() - app.extensions["devtrack_started_at"]
        return jsonify(uptime_seconds=round(elapsed, 3))

    @app.get("/health/ready")
    def readiness():
        return jsonify(status="ready", service="DevTrack", database="connected", event_count=count_events(app.config["DATABASE"]))

    @app.post("/events")
    def create_dashboard_event():
        title = request.form.get("title", "").strip()
        if not title:
            return redirect(url_for("dashboard", error="title-required"))
        if title:
            create_event(
                app.config["DATABASE"], title[:120],
                request.form.get("details", "")[:2000],
                request.form.get("category", "note")[:40],
                request.form.get("severity", "normal"),
            )
        return redirect(url_for("dashboard"))

    @app.post("/monitors")
    def create_dashboard_monitor():
        name = request.form.get("name", "").strip()
        url = request.form.get("url", "").strip()
        parsed_url = urlsplit(url) if url else None
        try:
            interval = int(request.form.get("interval_seconds", "300"))
        except ValueError:
            interval = 0
        if not name or not parsed_url or parsed_url.scheme not in {"http", "https"} or not parsed_url.hostname or interval < 30:
            return redirect(url_for("dashboard", monitor_error="invalid"))
        create_monitor(app.config["DATABASE"], name[:120], url[:2048], interval)
        return redirect(url_for("dashboard", monitor_created="1"))

    @app.get("/")
    def dashboard():
        query = request.args.get("q", "")[:100]
        category = request.args.get("category", "")[:40]
        severity = request.args.get("severity", "")[:10]
        try:
            page = max(1, int(request.args.get("page", "1")))
        except ValueError:
            page = 1
        page_size = 20
        offset = (page - 1) * page_size
        entries = filter_events(app.config["DATABASE"], query, category, severity, page_size + 1, offset)
        has_next = len(entries) > page_size
        entries = entries[:page_size]
        filters = {key: request.args[key] for key in ("q", "category", "severity") if request.args.get(key)}
        return render_template("index.html", events=entries, query=query, categories=list_categories(app.config["DATABASE"]), category_options=sorted(set(list_categories(app.config["DATABASE"])) | {"note", "build", "fix", "decision"}, key=str.casefold), selected_category=category, selected_severity=severity, event_count=count_events(app.config["DATABASE"]), category_count=len(list_categories(app.config["DATABASE"])), monitors=list_monitors(app.config["DATABASE"]), page=page, has_next=has_next, filters=filters)

    return app
