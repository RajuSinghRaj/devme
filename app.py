from datetime import datetime, timezone
import os
import time
from pathlib import Path

from database import initialize

from flask import Flask, jsonify, render_template


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
