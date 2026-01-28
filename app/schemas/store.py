"""Storefront request schemas."""

from __future__ import annotations
from pydantic import Field

from .common import DefaultModel

class WishlistRequest(DefaultModel):
    product_id: int = Field(gt=0)
