from __future__ import annotations
from decimal import Decimal
from datetime import datetime
from pydantic import Field
from .common import DefaultModel, Pagination
from ..models.enums import OrderStatus, FulfillmentType, PickedStatus

class OrderItemResponse(DefaultModel):
    id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=100)
    sku: str = Field(min_length=2, max_length=30)
    unit_price: Decimal = Field(ge=0, le=100000)
    quantity: int = Field(ge=0, le=10000)
    picked_status: PickedStatus

class OrderResponse(DefaultModel):
    id: int = Field(gt=0)
    order_number: str = Field(min_length=2, max_length=30)
    total_amount: Decimal = Field(ge=0, le=100000)
    status: OrderStatus
    fulfillment_type: FulfillmentType
    created_at: datetime
    items: list[OrderItemResponse]

class OrderListResponse(DefaultModel):
    orders: list[OrderResponse]
    pagination: Pagination

class CancelOrderResponse(DefaultModel):
    order_id: int = Field(gt=0)
    canceled_at: datetime
    status: OrderStatus = Field(default=OrderStatus.CANCELED)
