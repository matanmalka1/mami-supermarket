"""API DTO package."""

from .auth import AuthResponse, ChangePasswordRequest, LoginRequest, RegisterRequest, UserResponse
from .audit import AuditQuery, AuditResponse
from .cart import CartItemResponse, CartItemUpsertRequest, CartResponse
from .catalog import (
    AutocompleteItem,
    AutocompleteResponse,
    CategoryResponse,
    ProductResponse,
    ProductSearchResponse,
)
from .checkout import (
    CheckoutConfirmRequest,
    CheckoutConfirmResponse,
    CheckoutPreviewRequest,
    CheckoutPreviewResponse,
)
from .common import DefaultModel, ErrorResponse, PaginatedResponse, Pagination
from .orders import CancelOrderResponse, OrderListResponse, OrderResponse
from .ops import OpsOrderResponse, OpsOrdersQuery, UpdateOrderStatusRequest, UpdatePickStatusRequest
from .stock_requests import (
    BulkReviewItem,
    BulkReviewRequest,
    StockRequestCreateRequest,
    StockRequestResponse,
    StockRequestReviewRequest,
)

__all__ = [
    "DefaultModel",
    "ErrorResponse",
    "Pagination",
    "PaginatedResponse",
    "RegisterRequest",
    "LoginRequest",
    "ChangePasswordRequest",
    "UserResponse",
    "AuthResponse",
    "CategoryResponse",
    "ProductResponse",
    "ProductSearchResponse",
    "AutocompleteItem",
    "AutocompleteResponse",
    "CartItemUpsertRequest",
    "CartItemResponse",
    "CartResponse",
    "CheckoutPreviewRequest",
    "CheckoutPreviewResponse",
    "CheckoutConfirmRequest",
    "CheckoutConfirmResponse",
    "OrderItemResponse",
    "OrderResponse",
    "OrderListResponse",
    "CancelOrderResponse",
    "OpsOrdersQuery",
    "OpsOrderResponse",
    "UpdatePickStatusRequest",
    "UpdateOrderStatusRequest",
    "StockRequestCreateRequest",
    "StockRequestReviewRequest",
    "BulkReviewRequest",
    "BulkReviewItem",
    "StockRequestResponse",
    "AuditQuery",
    "AuditResponse",
]
