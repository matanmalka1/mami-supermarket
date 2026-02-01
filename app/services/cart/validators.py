"""Cart validation helpers."""

from __future__ import annotations
from flask import current_app
from sqlalchemy import select, func

from ...extensions import db
from ...middleware.error_handler import DomainError
from ...models import Inventory, Product
from ...services.branch import BranchCoreService


def validate_product(product_id: int) -> Product:
    """Validate product exists and is active."""
    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        raise DomainError("PRODUCT_INACTIVE", "Product is inactive or missing", status_code=404)
    return product


def assert_in_stock_anywhere(product: Product) -> None:
    """Assert product has stock in any branch."""
    total_available = db.session.scalar(
        select(func.coalesce(func.sum(Inventory.available_quantity), 0))
        .where(Inventory.product_id == product.id)
    )
    if total_available is None or total_available <= 0:
        raise DomainError("OUT_OF_STOCK_ANYWHERE", "Product is out of stock")


def assert_in_stock_delivery_branch(product: Product, required_quantity: int) -> None:
    """Assert product has sufficient stock in delivery branch."""
    branch_id = get_delivery_source_branch_id()
    branch_available = db.session.scalar(
        select(func.coalesce(func.sum(Inventory.available_quantity), 0))
        .where(Inventory.product_id == product.id, Inventory.branch_id == branch_id)
    )
    if branch_available is None or branch_available < required_quantity:
        raise DomainError(
            "OUT_OF_STOCK_DELIVERY_BRANCH",
            "Product is out of stock in the delivery warehouse",
            status_code=409,
        )


def get_delivery_source_branch_id() -> int:
    """Get the delivery source branch ID from config."""
    source_id = current_app.config.get("DELIVERY_SOURCE_BRANCH_ID", "")
    branch = BranchCoreService.ensure_delivery_source_branch_exists(source_id)
    return branch.id
