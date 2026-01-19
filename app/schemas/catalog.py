"""Catalog read models for categories and products."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from .common import DefaultModel, Pagination, PaginatedResponse


class CategoryResponse(DefaultModel):
    id: UUID
    name: str
    description: str | None
    is_active: bool = True


class ProductResponse(DefaultModel):
    id: UUID
    name: str
    sku: str
    price: Decimal
    description: str | None
    category_id: UUID
    is_active: bool
    in_stock_anywhere: bool
    in_stock_for_branch: bool | None = None


class ProductSearchResponse(DefaultModel):
    items: list[ProductResponse]
    pagination: Pagination


class AutocompleteItem(DefaultModel):
    id: UUID
    name: str


class AutocompleteResponse(Pagination):
    items: list[AutocompleteItem]
