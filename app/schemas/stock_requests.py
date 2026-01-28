from __future__ import annotations
from datetime import datetime

from pydantic import Field
from .common import DefaultModel
from ..models.enums import StockRequestStatus, StockRequestType

class StockRequestCreateRequest(DefaultModel):
    branch_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=10000)
    request_type: StockRequestType

class StockRequestReviewRequest(DefaultModel):
    status: StockRequestStatus
    approved_quantity: int | None = Field(default=None, gt=0, le=10000)
    rejection_reason: str | None = Field(default=None, min_length=2, max_length=200)

class BulkReviewItem(DefaultModel):
    request_id: int = Field(gt=0)
    status: StockRequestStatus
    approved_quantity: int | None = Field(default=None, gt=0, le=10000)
    rejection_reason: str | None = Field(default=None, min_length=2, max_length=200)

class BulkReviewRequest(DefaultModel):
    items: list[BulkReviewItem]

class StockRequestResponse(DefaultModel):
    id: int
    branch_id: int
    branch_name: str | None = None
    product_id: int
    product_name: str | None = None
    product_sku: str | None = None
    quantity: int
    request_type: StockRequestType
    status: StockRequestStatus
    actor_user_id: int
    created_at: datetime
