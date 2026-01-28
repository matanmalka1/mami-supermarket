"""Extension registration (DB, JWT, limiter)."""

from flask import current_app ,request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
jwt = JWTManager()

def _skip_options() -> bool:
    return request.method == "OPTIONS"



def get_rate_limit_defaults():
    limits = current_app.config.get("RATE_LIMIT_DEFAULTS", "200 per day, 50 per hour")
    return tuple(limit.strip() for limit in limits.split(",") if limit.strip())

lim_defaults = get_rate_limit_defaults()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=lim_defaults,
)
limiter.request_filter = _skip_options
