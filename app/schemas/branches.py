from __future__ import annotations
from datetime import time

from typing import Optional
from pydantic import Field
from .common import DefaultModel, Pagination

class BranchResponse(DefaultModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=100)
    address: str = Field(min_length=5, max_length=200)
    is_active: bool

class DeliverySlotResponse(DefaultModel):
    id: int = Field(gt=0)
    branch_id: int = Field(gt=0)
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time

class InventoryResponse(DefaultModel):
    id: int = Field(gt=0)
    branch_id: int = Field(gt=0)
    branch_name: str = Field(min_length=2, max_length=100)
    product_id: int = Field(gt=0)
    product_name: str = Field(min_length=2, max_length=100)
    product_sku: str = Field(min_length=2, max_length=30)
    available_quantity: int = Field(ge=0, le=100000)
    reserved_quantity: int = Field(ge=0, le=100000)
    limit: int = Field(ge=0, le=10000)
    offset: int = Field(ge=0, le=100000)
    total: int = Field(ge=0, le=100000)

class InventoryListResponse(DefaultModel):
    items: list[InventoryResponse]
    pagination: Pagination

class InventoryUpdateRequest(DefaultModel):
    available_quantity: int = Field(ge=0)
    reserved_quantity: int = Field(ge=0)

class InventoryCreateRequest(DefaultModel):
    product_id: int
    branch_id: int
    available_quantity: int = Field(ge=0)
    reserved_quantity: int = Field(ge=0)

class BranchAdminRequest(DefaultModel):
    name: str
    address: str

class DeliverySlotAdminRequest(DefaultModel):
    branch_id: int
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time

class BranchesQuery(DefaultModel):
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class DeliverySlotsQuery(DefaultModel):
    dayOfWeek: Optional[int] = Field(default=None, ge=0, le=6)
    branchId: Optional[int] = None
