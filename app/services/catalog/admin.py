"""Catalog admin service facade."""

from __future__ import annotations

from app.schemas.catalog import CategoryResponse, ProductResponse
from . import category_admin, product_admin


class CatalogAdminService:
    """Facade for catalog admin operations."""

    @staticmethod
    def create_category(name: str, description: str | None) -> CategoryResponse:
        return category_admin.create_category(name, description)

    @staticmethod
    def update_category(
        category_id: int, name: str, description: str | None
    ) -> CategoryResponse:
        return category_admin.update_category(category_id, name, description)

    @staticmethod
    def toggle_category(category_id: int, active: bool) -> CategoryResponse:
        return category_admin.toggle_category(category_id, active)

    @staticmethod
    def create_product(
        name: str,
        sku: str,
        price: str,
        category_id: int,
        description: str | None,
    ) -> ProductResponse:
        return product_admin.create_product(name, sku, price, category_id, description)

    @staticmethod
    def update_product(
        product_id: int,
        name: str | None,
        sku: str | None,
        price: str | None,
        category_id: int | None,
        description: str | None,
    ) -> ProductResponse:
        return product_admin.update_product(
            product_id, name, sku, price, category_id, description
        )

    @staticmethod
    def toggle_product(product_id: int, active: bool) -> ProductResponse:
        return product_admin.toggle_product(product_id, active)
