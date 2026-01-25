"""Storefront request schemas."""

from __future__ import annotations
from uuid import UUID

from .common import DefaultModel


class WishlistRequest(DefaultModel):
    product_id: UUID
