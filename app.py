from datetime import datetime, timezone

from flask import Flask, jsonify, render_template


def create_app(test_config=None):
    """Create and configure the DevTrack Flask application."""
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="devtrack-local-key",
        TESTING=False,
    )
    if test_config:
        app.config.update(test_config)

    @app.context_processor
    def inject_now():
        return {"current_year": datetime.now(timezone.utc).year}

    @app.get("/health")
    def health():
        return jsonify(status="ok", service="DevTrack")

    @app.get("/")
    def dashboard():
        return render_template("index.html")

    return app
