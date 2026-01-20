"""Middleware package helpers."""

from .error_handler import register_error_handlers
from .request_id import register_request_id


def register_middlewares(app) -> None:
    register_request_id(app)
    register_error_handlers(app)
