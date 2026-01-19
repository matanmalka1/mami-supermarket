"""Application factory and package definition for Mami Supermarket backend."""

from flask import Flask

from .config import AppConfig
from .extensions import db, jwt
from .middleware import register_middlewares
from .utils.logging_config import setup_structured_logging


def create_app(config: AppConfig | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        instance_relative_config=False,
        static_folder=None,
    )
    cfg = config or AppConfig()
    app.config.from_mapping(vars(cfg))

    setup_structured_logging(app)
    _register_extensions(app)
    register_middlewares(app)
    _register_blueprints(app)

    return app


def _register_extensions(app: Flask) -> None:
    db.init_app(app)
    jwt.init_app(app)


def _register_blueprints(app: Flask) -> None:
    from .routes.v1 import (
        admin,
        auth,
        cart,
        catalog,
        checkout,
        ops,
        orders,
    )

    app.register_blueprint(auth.blueprint, url_prefix="/api/v1/auth")
    app.register_blueprint(catalog.blueprint, url_prefix="/api/v1/catalog")
    app.register_blueprint(cart.blueprint, url_prefix="/api/v1/cart")
    app.register_blueprint(checkout.blueprint, url_prefix="/api/v1/checkout")
    app.register_blueprint(orders.blueprint, url_prefix="/api/v1/orders")
    app.register_blueprint(ops.blueprint, url_prefix="/api/v1/ops")
    app.register_blueprint(admin.blueprint, url_prefix="/api/v1/admin")
