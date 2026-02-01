from __future__ import annotations
from decimal import Decimal
from pydantic import Field

from .common import DefaultModel

class CartItemUpsertRequest(DefaultModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=10000)

class CartItemResponse(DefaultModel):
    id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=10000)
    unit_price: Decimal = Field(ge=0, le=100000)
    product_name: str | None = None
    product_image: str | None = None

class CartResponse(DefaultModel):
    id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    total_amount: Decimal = Field(ge=0, le=100000)
    items: list[CartItemResponse]
