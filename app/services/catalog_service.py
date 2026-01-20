"""Catalog read and admin services split by responsibility."""

from __future__ import annotations
from typing import Sequence
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Category, Inventory, Product
from app.schemas.catalog import (
    AutocompleteItem,
    AutocompleteResponse,
    CategoryResponse,
    ProductResponse,
)
from app.services.audit_service import AuditService

def _to_category_response(category: Category) -> CategoryResponse:
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        is_active=category.is_active,
    )

def _load_inventory(product: Product) -> None:
    if not product.inventory:
        product.inventory = (
            db.session.execute(sa.select(Inventory).where(Inventory.product_id == product.id)).scalars().all()
        )

def _matches_stock(product: Product, branch_id: UUID | None, desired: bool) -> bool:
    _load_inventory(product)
    if branch_id:
        row = next((i for i in product.inventory if i.branch_id == branch_id), None)
        quantity = row.available_quantity if row else 0
    else:
        quantity = sum(i.available_quantity for i in product.inventory)
    return (quantity > 0) == desired

def _to_product_response(product: Product, branch_id: UUID | None) -> ProductResponse:
    _load_inventory(product)
    branch_available: bool | None = None
    if branch_id:
        row = next((i for i in product.inventory if i.branch_id == branch_id), None)
        branch_available = bool(row and row.available_quantity > 0)
    return ProductResponse(
        id=product.id,
        name=product.name,
        sku=product.sku,
        price=product.price,
        description=product.description,
        category_id=product.category_id,
        is_active=product.is_active,
        in_stock_anywhere=any(i.available_quantity > 0 for i in product.inventory),
        in_stock_for_branch=branch_available,
    )

def _map_products(items: Sequence[Product], branch_id: UUID | None) -> list[ProductResponse]:
    return [_to_product_response(item, branch_id) for item in items]

class CatalogQueryService:
    @staticmethod
    def list_categories(limit: int, offset: int) -> tuple[list[CategoryResponse], int]:
        stmt = sa.select(Category).where(Category.is_active.is_(True)).offset(offset).limit(limit)
        categories = db.session.execute(stmt).scalars().all()
        total = db.session.scalar(sa.select(sa.func.count()).select_from(Category).where(Category.is_active.is_(True)))
        return ([_to_category_response(c) for c in categories], total or 0)

    @staticmethod
    def get_category_products(
        category_id: UUID,
        branch_id: UUID | None,
        limit: int,
        offset: int,
    ) -> tuple[list[ProductResponse], int]:
        stmt = (
            sa.select(Product)
            .where(Product.category_id == category_id)
            .where(Product.is_active.is_(True))
            .options(selectinload(Product.inventory).selectinload(Inventory.branch))
            .offset(offset)
            .limit(limit)
        )
        products = db.session.execute(stmt).scalars().all()
        total = db.session.scalar(
            sa.select(sa.func.count())
            .select_from(Product)
            .where(Product.category_id == category_id)
            .where(Product.is_active.is_(True))
        )
        return _map_products(products, branch_id), total or 0

    @staticmethod
    def get_product(product_id: UUID, branch_id: UUID | None) -> ProductResponse:
        stmt = sa.select(Product).where(Product.id == product_id).options(selectinload(Product.inventory).selectinload(Inventory.branch))
        product = db.session.execute(stmt).scalar_one_or_none()
        if not product or not product.is_active:
            raise DomainError("NOT_FOUND", "Product not found", status_code=404)
        return _to_product_response(product, branch_id)

    @staticmethod
    def search_products(
        query: str | None,
        category_id: UUID | None,
        in_stock: bool | None,
        branch_id: UUID | None,
        limit: int,
        offset: int,
    ) -> tuple[list[ProductResponse], int]:
        base = sa.select(Product).where(Product.is_active.is_(True))
        if query:
            base = base.where(Product.name.ilike(f"%{query}%"))
        if category_id:
            base = base.where(Product.category_id == category_id)
        stmt = base.options(selectinload(Product.inventory).selectinload(Inventory.branch)).offset(offset).limit(limit)
        products = db.session.execute(stmt).scalars().all()
        if in_stock is not None:
            products = [p for p in products if _matches_stock(p, branch_id, in_stock)]
        count_stmt = sa.select(sa.func.count()).select_from(base.subquery())
        total = len(products) if in_stock is not None else db.session.scalar(count_stmt)
        return _map_products(products, branch_id), total or 0

    @staticmethod
    def autocomplete(query: str | None, limit: int) -> AutocompleteResponse:
        stmt = sa.select(Product).where(Product.is_active.is_(True))
        if query:
            stmt = stmt.where(Product.name.ilike(f"%{query}%"))
        products = db.session.execute(stmt.limit(limit)).scalars().all()
        items = [AutocompleteItem(id=p.id, name=p.name) for p in products]
        return AutocompleteResponse(total=len(items), limit=limit, offset=0, items=items)


class CatalogAdminService:
    @staticmethod
    def create_category(name: str, description: str | None) -> CategoryResponse:
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        AuditService.log_event(entity_type="category", action="CREATE", entity_id=category.id)
        return _to_category_response(category)

    @staticmethod
    def update_category(category_id: UUID, name: str, description: str | None) -> CategoryResponse:
        category = db.session.get(Category, category_id)
        if not category:
            raise DomainError("NOT_FOUND", "Category not found", status_code=404)
        old_value = {"name": category.name, "description": category.description}
        category.name = name
        category.description = description
        db.session.add(category)
        db.session.commit()
        AuditService.log_event(
            entity_type="category",
            action="UPDATE",
            entity_id=category.id,
            old_value=old_value,
            new_value={"name": name, "description": description},
        )
        return _to_category_response(category)

    @staticmethod
    def toggle_category(category_id: UUID, active: bool) -> CategoryResponse:
        category = db.session.get(Category, category_id)
        if not category:
            raise DomainError("NOT_FOUND", "Category not found", status_code=404)
        category.is_active = active
        db.session.add(category)
        db.session.commit()
        AuditService.log_event(
            entity_type="category",
            action="DEACTIVATE" if not active else "ACTIVATE",
            entity_id=category.id,
            new_value={"is_active": active},
        )
        return _to_category_response(category)

    @staticmethod
    def create_product(
        name: str,
        sku: str,
        price: str,
        category_id: UUID,
        description: str | None,
    ) -> ProductResponse:
        category = db.session.get(Category, category_id)
        if not category:
            raise DomainError("NOT_FOUND", "Category not found", status_code=404)
        product = Product(
            name=name,
            sku=sku,
            price=price,
            description=description,
            category_id=category_id,
        )
        try:
            db.session.add(product)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise DomainError(
                "DATABASE_ERROR",
                "Could not create product",
                details={"error": str(exc)},
            ) from exc
        AuditService.log_event(entity_type="product", action="CREATE", entity_id=product.id)
        return _to_product_response(product, None)

    @staticmethod
    def update_product(
        product_id: UUID,
        name: str | None,
        sku: str | None,
        price: str | None,
        category_id: UUID | None,
        description: str | None,
    ) -> ProductResponse:
        product = db.session.get(Product, product_id)
        if not product:
            raise DomainError("NOT_FOUND", "Product not found", status_code=404)
        old_value = {
            "name": product.name,
            "sku": product.sku,
            "price": str(product.price),
            "category_id": str(product.category_id),
            "description": product.description,
        }
        if name:
            product.name = name
        if sku:
            product.sku = sku
        if price:
            product.price = price
        if category_id:
            product.category_id = category_id
        if description is not None:
            product.description = description
        db.session.add(product)
        db.session.commit()
        AuditService.log_event(
            entity_type="product",
            action="UPDATE",
            entity_id=product.id,
            old_value=old_value,
            new_value={
                "name": product.name,
                "sku": product.sku,
                "price": str(product.price),
                "category_id": str(product.category_id),
                "description": product.description,
            },
        )
        return _to_product_response(product, None)

    @staticmethod
    def toggle_product(product_id: UUID, active: bool) -> ProductResponse:
        product = db.session.get(Product, product_id)
        if not product:
            raise DomainError("NOT_FOUND", "Product not found", status_code=404)
        product.is_active = active
        db.session.add(product)
        db.session.commit()
        AuditService.log_event(
            entity_type="product",
            action="DEACTIVATE" if not active else "ACTIVATE",
            entity_id=product.id,
            new_value={"is_active": active},
        )
        return _to_product_response(product, None)
