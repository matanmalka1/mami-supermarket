"""Teardown middleware to ensure scoped-session cleanup."""

from __future__ import annotations

from app.extensions import db


def register_db_session_teardown(app) -> None:
    """Remove scoped_session after each request/appcontext teardown."""

    @app.teardown_appcontext
    def cleanup_session(_exception=None):
        db.session.remove()
