def test_app_uses_configured_secret_key(tmp_path):
    from app import create_app
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "configured-test-secret",
        "DATABASE": str(tmp_path / "configured.sqlite"),
    })
    assert app.config["SECRET_KEY"] == "configured-test-secret"

def test_database_path_can_be_overridden(tmp_path):
    from app import create_app
    target = tmp_path / "custom.sqlite"
    app = create_app({"TESTING": True, "DATABASE": str(target)})
    assert target.exists()
    assert app.config["DATABASE"] == str(target)


def test_log_level_can_be_configured(tmp_path):
    from app import create_app
    app = create_app({"TESTING": True, "LOG_LEVEL": "WARNING", "DATABASE": str(tmp_path / "log.sqlite")})
    import logging
    assert app.logger.level == logging.WARNING


def test_session_cookie_defaults_are_secure(tmp_path):
    from app import create_app
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "cookies.sqlite")})
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
