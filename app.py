from datetime import datetime, timezone
import os
import time
from pathlib import Path

from database import initialize
from events import create_event, list_events

from flask import Flask, jsonify, render_template, request


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
        return {"current_year": datetime.now(timezone.utc).year}

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
        event_id = create_event(
            app.config["DATABASE"], title.strip(),
            str(payload.get("details", "")),
            str(payload.get("category", "note")),
            str(payload.get("severity", "normal")),
        )
        return jsonify(id=event_id), 201

    @app.get("/api/events")
    def api_events():
        try:
            limit = int(request.args.get("limit", "50"))
        except ValueError:
            return jsonify(error="limit must be an integer"), 400
        return jsonify(events=list_events(app.config["DATABASE"], limit=limit))

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

    @app.get("/")
    def dashboard():
        return render_template("index.html")

    return app
