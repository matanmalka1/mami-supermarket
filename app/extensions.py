"""Extension registration (DB, JWT, limiter)."""

from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
jwt = JWTManager()

def _skip_options() -> bool:
    return request.method == "OPTIONS"

limiter = Limiter(
    key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
)
limiter.request_filter = _skip_options
