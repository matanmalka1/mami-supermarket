from __future__ import annotations

from datetime import datetime
from sqlalchemy import select ,func
from sqlalchemy.orm import selectinload

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Order, OrderDeliveryDetails
from app.schemas.ops import OpsOrderResponse
from app.schemas.orders import OrderResponse
from app.services.shared_queries import SharedOperations
from .mappers import to_detail, to_ops_response


class OpsOrderQueryService:
    @staticmethod
    def list_orders(
        status,
        date_from: datetime | None,
        date_to: datetime | None,
        limit: int,
        offset: int,
    ) -> tuple[list[OpsOrderResponse], int]:
        stmt = select(Order).options(
            selectinload(Order.items),
            selectinload(Order.user),
            selectinload(Order.delivery).selectinload(OrderDeliveryDetails.delivery_slot),
        )
        
        # Build conditions for filtering
        conditions = {
            "status": (
                lambda: bool(status),
                Order.status == status if status else None,
            ),
            "date_from": (
                lambda: date_from is not None,
                Order.created_at >= date_from if date_from is not None else None,
            ),
            "date_to": (
                lambda: date_to is not None,
                Order.created_at <= date_to if date_to is not None else None,
            ),
        }
        
        stmt = SharedOperations.build_filtered_query(stmt, conditions)
        stmt = stmt.order_by(Order.created_at.asc())
        
        def transform(order):
            response = to_ops_response(order)
            return response
        
        responses, total = SharedOperations.paginate_query(
            base_query=stmt,
            model_class=Order,
            limit=limit,
            offset=offset,
            transform_fn=transform,
        )
        responses.sort(key=lambda o: o.urgency_rank)
        return responses, total

    @staticmethod
    def get_order(order_id: int) -> OrderResponse:
        order = OpsOrderQueryService._load_order(order_id)
        return to_detail(order)

    @staticmethod
    def _load_order(order_id: int) -> Order:
        order = db.session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.delivery).selectinload(OrderDeliveryDetails.delivery_slot),
            )
        ).scalar_one_or_none()
        if not order:
            raise DomainError("NOT_FOUND", "Order not found", status_code=404)
        return order
