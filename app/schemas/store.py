"""Storefront request schemas."""

from __future__ import annotations
from pydantic import Field

from .common import DefaultModel
from typing import Optional

class WishlistRequest(DefaultModel):
    product_id: int = Field(gt=0)

class WishlistQuery(DefaultModel):
    limit: Optional[int] = Field(default=50, ge=1, le=200)
    offset: Optional[int] = Field(default=0, ge=0)
