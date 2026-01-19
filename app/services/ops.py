"""Ops order workflows for employees/managers/admins."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import selectinload

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Order, OrderDeliveryDetails
from app.models.enums import OrderStatus, PickedStatus, Role
from app.schemas.ops import OpsOrderResponse
from app.schemas.orders import OrderItemResponse, OrderResponse
from app.services.audit import AuditService


class OpsOrderService:
    @staticmethod
    def list_orders(
        status: OrderStatus | None,
        date_from: datetime | None,
        date_to: datetime | None,
        limit: int,
        offset: int,
    ) -> tuple[list[OpsOrderResponse], int]:
        base = sa.select(Order)
        stmt = base.options(
            selectinload(Order.items),
            selectinload(Order.delivery).selectinload(OrderDeliveryDetails.delivery_slot),
        )
        if status:
            base = base.where(Order.status == status)
            stmt = stmt.where(Order.status == status)
        if date_from:
            base = base.where(Order.created_at >= date_from)
            stmt = stmt.where(Order.created_at >= date_from)
        if date_to:
            base = base.where(Order.created_at <= date_to)
            stmt = stmt.where(Order.created_at <= date_to)
        stmt = stmt.order_by(Order.created_at.asc())
        total = db.session.scalar(sa.select(sa.func.count()).select_from(base.subquery()))
        rows = db.session.execute(stmt.offset(offset).limit(limit)).scalars().all()
        responses = [OpsOrderService._to_ops_response(order) for order in rows]
        responses.sort(key=lambda o: o.urgency_rank)
        return responses, total or 0

    @staticmethod
    def get_order(order_id: UUID) -> OrderResponse:
        order = OpsOrderService._load_order(order_id)
        return OpsOrderService._to_detail(order)

    @staticmethod
    def update_item_status(
        order_id: UUID,
        item_id: UUID,
        picked_status: str,
        actor_id: UUID,
    ) -> OrderResponse:
        session = db.session
        order = session.execute(
            sa.select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
            .with_for_update()
        ).scalar_one_or_none()
        if not order:
            raise DomainError("NOT_FOUND", "Order not found", status_code=404)
        item = next((i for i in order.items if i.id == item_id), None)
        if not item:
            raise DomainError("NOT_FOUND", "Order item not found", status_code=404)
        try:
            new_status = PickedStatus(picked_status)
        except ValueError:
            raise DomainError("BAD_REQUEST", "Invalid picked status", status_code=400)
        old_value = {"picked_status": item.picked_status.value}
        item.picked_status = new_status
        session.add(item)
        AuditService.log_event(
            entity_type="order_item",
            action="UPDATE_PICK_STATUS",
            actor_user_id=actor_id,
            entity_id=item.id,
            old_value=old_value,
            new_value={"picked_status": new_status.value},
        )
        session.commit()
        return OpsOrderService._to_detail(order)

    @staticmethod
    def update_order_status(
        order_id: UUID,
        status_value: str,
        actor_id: UUID,
        actor_role: Role,
    ) -> OrderResponse:
        session = db.session
        order = session.execute(
            sa.select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
            .with_for_update()
        ).scalar_one_or_none()
        if not order:
            raise DomainError("NOT_FOUND", "Order not found", status_code=404)
        try:
            new_status = OrderStatus(status_value)
        except ValueError:
            raise DomainError("BAD_REQUEST", "Invalid status", status_code=400)
        if not OpsOrderService._can_transition(order, new_status, actor_role):
            raise DomainError("INVALID_STATUS_TRANSITION", "Status transition not allowed", status_code=409)
        old_value = {"status": order.status.value}
        order.status = new_status
        session.add(order)
        AuditService.log_event(
            entity_type="order",
            action="UPDATE_STATUS",
            actor_user_id=actor_id,
            entity_id=order.id,
            old_value=old_value,
            new_value={"status": order.status.value},
        )
        session.commit()
        return OpsOrderService._to_detail(order)

    @staticmethod
    def _can_transition(order: Order, new_status: OrderStatus, actor_role: Role) -> bool:
        current = order.status
        if actor_role in {Role.MANAGER, Role.ADMIN}:
            return True
        if actor_role == Role.EMPLOYEE:
            if current == OrderStatus.CREATED and new_status == OrderStatus.IN_PROGRESS:
                return True
            if current == OrderStatus.IN_PROGRESS and new_status == OrderStatus.READY:
                all_picked = all(item.picked_status == PickedStatus.PICKED for item in order.items)
                return all_picked
            if current == OrderStatus.IN_PROGRESS and new_status == OrderStatus.MISSING:
                any_missing = any(item.picked_status == PickedStatus.MISSING for item in order.items)
                return any_missing
        return False

    @staticmethod
    def _load_order(order_id: UUID) -> Order:
        order = db.session.execute(
            sa.select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.delivery).selectinload(OrderDeliveryDetails.delivery_slot),
            )
        ).scalar_one_or_none()
        if not order:
            raise DomainError("NOT_FOUND", "Order not found", status_code=404)
        return order

    @staticmethod
    def _to_ops_response(order: Order) -> OpsOrderResponse:
        pending_count = sum(1 for item in order.items if item.picked_status != PickedStatus.PICKED)
        urgency_rank = OpsOrderService._urgency_rank(order)
        return OpsOrderResponse(
            order_id=order.id,
            order_number=order.order_number,
            status=order.status,
            urgency_rank=urgency_rank,
            created_at=order.created_at,
            items_pending=pending_count,
        )

    @staticmethod
    def _to_detail(order: Order) -> OrderResponse:
        items = [
            OrderItemResponse(
                product_id=item.product_id,
                name=item.name,
                sku=item.sku,
                unit_price=item.unit_price,
                quantity=item.quantity,
                picked_status=item.picked_status,
            )
            for item in order.items
        ]
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            total_amount=order.total_amount,
            status=order.status,
            fulfillment_type=order.fulfillment_type,
            created_at=order.created_at,
            items=items,
        )

    @staticmethod
    def _urgency_rank(order: Order) -> int:
        if order.delivery and order.delivery.delivery_slot:
            start = order.delivery.delivery_slot.start_time
            return (start.hour * 60 + start.minute) if start else 24 * 60
        return 24 * 60
