from datetime import datetime, timezone
import os
import time
from pathlib import Path

from database import initialize
from events import create_event, delete_event, list_events, search_events, update_event

from flask import Flask, jsonify, redirect, render_template, request, url_for


def create_app(test_config=None):
    """Create and configure the DevTrack Flask application."""
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("DEVTRACK_SECRET_KEY", "devtrack-local-key"),
        TESTING=False,
        DATABASE=os.environ.get("DEVTRACK_DATABASE", str(Path(app.instance_path) / "devtrack.sqlite")),
    )
    if test_config:
        app.config.update(test_config)
    initialize(app.config["DATABASE"])

    @app.context_processor
    def inject_now():
        now = datetime.now(timezone.utc)
        return {"current_year": now.year, "today_label": f"{now:%A, %B} {now.day}"}

    app.extensions["devtrack_started_at"] = time.monotonic()

    @app.get("/health")
    def health():
        return jsonify(status="ok", service="DevTrack")

    @app.post("/api/events")
    def api_create_event():
        payload = request.get_json(silent=True) or {}
        title = payload.get("title", "")
        if not isinstance(title, str) or not title.strip():
            return jsonify(error="title is required"), 400
        severity = payload.get("severity", "normal")
        if severity not in {"low", "normal", "high"}:
            return jsonify(error="severity must be low, normal, or high"), 400
        event_id = create_event(
            app.config["DATABASE"], title.strip()[:120],
            str(payload.get("details", ""))[:2000],
            str(payload.get("category", "note"))[:40],
            severity,
        )
        return jsonify(id=event_id), 201

    @app.put("/api/events/<int:event_id>")
    def api_update_event(event_id):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="JSON object required"), 400
        title = payload.get("title")
        severity = payload.get("severity", "normal")
        if not isinstance(title, str) or not title.strip():
            return jsonify(error="title is required"), 400
        if severity not in {"low", "normal", "high"}:
            return jsonify(error="invalid severity"), 400
        updated = update_event(
            app.config["DATABASE"], event_id, title.strip()[:120],
            str(payload.get("details", ""))[:2000],
            str(payload.get("category", "note"))[:40], severity,
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

    @app.get("/api/events")
    def api_events():
        try:
            limit = int(request.args.get("limit", "50"))
        except ValueError:
            return jsonify(error="limit must be an integer"), 400
        query = request.args.get("q", "")[:100]
        entries = search_events(app.config["DATABASE"], query, limit) if query else list_events(app.config["DATABASE"], limit)
        return jsonify(events=entries)

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
        return jsonify(status="ready", service="DevTrack")

    @app.post("/events")
    def create_dashboard_event():
        title = request.form.get("title", "").strip()
        if title:
            create_event(
                app.config["DATABASE"], title[:120],
                request.form.get("details", "")[:2000],
                request.form.get("category", "note")[:40],
            )
        return redirect(url_for("dashboard"))

    @app.get("/")
    def dashboard():
        query = request.args.get("q", "")[:100]
        entries = search_events(app.config["DATABASE"], query) if query else list_events(app.config["DATABASE"])
        return render_template("index.html", events=entries, query=query)

    return app
