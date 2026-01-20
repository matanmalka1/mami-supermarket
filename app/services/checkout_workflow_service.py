"""Checkout workflow helpers split by responsibility."""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, time
from decimal import Decimal
import hashlib
import json
from uuid import UUID, uuid4
from flask import current_app
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import (
    Branch,
    Cart,
    CartItem,
    DeliverySlot,
    IdempotencyKey,
    Inventory,
    Order,
    OrderDeliveryDetails,
    OrderItem,
    OrderPickupDetails,
)
from app.models.enums import FulfillmentType, OrderStatus
from app.schemas.checkout import CheckoutConfirmRequest, CheckoutConfirmResponse, MissingItem
from app.services.audit_service import AuditService
from app.services.branch_service import BranchService

@dataclass
class CheckoutTotals:
    cart_total: Decimal
    delivery_fee: Decimal | None
    total_amount: Decimal

class CheckoutBranchValidator:
    @staticmethod
    def resolve_branch(fulfillment_type: FulfillmentType | None, branch_id: UUID | None) -> UUID:
        if fulfillment_type == FulfillmentType.DELIVERY:
            source_id = current_app.config.get("DELIVERY_SOURCE_BRANCH_ID", "")
            branch = BranchService.ensure_delivery_source_branch_exists(source_id)
            return branch.id
        if branch_id:
            branch = db.session.get(Branch, branch_id)
            if not branch or not branch.is_active:
                raise DomainError("NOT_FOUND", "Branch not found", status_code=404)
            return branch.id
        raise DomainError("BAD_REQUEST", "Branch is required for pickup", status_code=400)

    @staticmethod
    def validate_delivery_slot(fulfillment_type: FulfillmentType | None, slot_id: UUID | None, branch_id: UUID) -> None:
        if fulfillment_type != FulfillmentType.DELIVERY:
            return
        if not slot_id:
            raise DomainError("BAD_REQUEST", "Delivery slot is required for delivery", status_code=400)
        slot = db.session.get(DeliverySlot, slot_id)
        if not slot or not slot.is_active:
            raise DomainError("NOT_FOUND", "Delivery slot not found", status_code=404)
        if slot.branch_id != branch_id:
            raise DomainError("INVALID_SLOT", "Delivery slot does not belong to delivery branch", status_code=400)
        start = slot.start_time
        end = slot.end_time
        if not (time(6, 0) <= start < end <= time(22, 0)) or (end.hour - start.hour) != 2:
            raise DomainError("INVALID_SLOT", "Delivery slot must be a 2-hour window between 06:00-22:00", status_code=400)


class CheckoutCartLoader:
    @staticmethod
    def load(cart_id: UUID, for_update: bool = False) -> Cart:
        stmt = select(Cart).where(Cart.id == cart_id).options(joinedload(Cart.items).joinedload(CartItem.product))
        if for_update:
            stmt = stmt.with_for_update()
        cart = db.session.execute(stmt).unique().scalar_one_or_none()
        if not cart:
            raise DomainError("NOT_FOUND", "Cart not found", status_code=404)
        return cart

class CheckoutPricing:
    @staticmethod
    def calculate(cart: Cart, fulfillment_type: FulfillmentType | None) -> CheckoutTotals:
        cart_total = sum(item.unit_price * item.quantity for item in cart.items)
        if fulfillment_type == FulfillmentType.DELIVERY:
            min_total = Decimal(str(current_app.config.get("DELIVERY_MIN_TOTAL", 150)))
            under_min_fee = Decimal(str(current_app.config.get("DELIVERY_FEE_UNDER_MIN", 30)))
            delivery_fee: Decimal | None = Decimal("0") if cart_total >= min_total else under_min_fee
        else:
            delivery_fee = None
        total_amount = cart_total + (delivery_fee or Decimal("0"))
        return CheckoutTotals(cart_total=cart_total, delivery_fee=delivery_fee, total_amount=total_amount)

class CheckoutIdempotencyManager:
    @staticmethod
    def hash_request(payload: CheckoutConfirmRequest) -> str:
        data = payload.model_dump()
        data.pop("idempotency_key", None)
        return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode("utf-8")).hexdigest()

    @staticmethod
    def get_existing(user_id: UUID, key: str, request_hash: str) -> IdempotencyKey | None:
        existing = db.session.execute(
            select(IdempotencyKey).where(
                IdempotencyKey.user_id == user_id,
                IdempotencyKey.key == key,
            )
        ).scalar_one_or_none()
        if not existing:
            return None
        if existing.request_hash != request_hash:
            raise DomainError("IDEMPOTENCY_CONFLICT", "Request payload differs for same Idempotency-Key", status_code=409)
        return existing

    @staticmethod
    def store_response(user_id: UUID, key: str, request_hash: str, response: CheckoutConfirmResponse) -> None:
        record = IdempotencyKey(
            id=uuid4(),
            user_id=user_id,
            key=key,
            request_hash=request_hash,
            response_payload=response.model_dump(),
            status_code=201,
        )
        db.session.add(record)
        db.session.commit()


class CheckoutInventoryManager:
    def __init__(self, branch_id: UUID):
        self.branch_id = branch_id

    def lock_inventory(self, cart_items) -> dict[tuple[UUID, UUID], Inventory]:
        inv_ids = [item.product_id for item in cart_items]
        inventory_rows = (
            db.session.execute(
                select(Inventory)
                .where(Inventory.product_id.in_(inv_ids))
                .where(Inventory.branch_id == self.branch_id)
                .with_for_update()
            )
            .scalars()
            .all()
        )
        return {(inv.product_id, inv.branch_id): inv for inv in inventory_rows}

    def missing_items(self, cart_items, inv_map=None) -> list[MissingItem]:
        missing: list[MissingItem] = []
        for item in cart_items:
            if inv_map is None:
                inv_row = db.session.execute(
                    select(Inventory).where(Inventory.product_id == item.product_id, Inventory.branch_id == self.branch_id)
                ).scalar_one_or_none()
            else:
                inv_row = inv_map.get((item.product_id, self.branch_id))
            available = inv_row.available_quantity if inv_row else 0
            if available < item.quantity:
                missing.append(
                    MissingItem(
                        product_id=item.product_id,
                        requested_quantity=item.quantity,
                        available_quantity=available,
                    )
                )
        return missing

    def decrement_inventory(self, cart_items, inv_map) -> None:
        for item in cart_items:
            key = (item.product_id, self.branch_id)
            inv_row = inv_map.get(key)
            if not inv_row:
                continue
            old_value = {
                "available_quantity": inv_row.available_quantity,
                "reserved_quantity": inv_row.reserved_quantity,
            }
            inv_row.available_quantity -= item.quantity
            db.session.add(inv_row)
            AuditService.log_event(
                entity_type="inventory",
                action="DECREMENT",
                entity_id=inv_row.id,
                old_value=old_value,
                new_value={
                    "available_quantity": inv_row.available_quantity,
                    "reserved_quantity": inv_row.reserved_quantity,
                },
            )


class CheckoutOrderBuilder:
    @staticmethod
    def order_number() -> str:
        return f"ORD-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:6].upper()}"

    @staticmethod
    def create_order(cart: Cart, payload: CheckoutConfirmRequest, branch_id: UUID, total_amount: Decimal) -> Order:
        order = Order(
            id=uuid4(),
            order_number=CheckoutOrderBuilder.order_number(),
            user_id=cart.user_id,
            total_amount=total_amount,
            fulfillment_type=payload.fulfillment_type or FulfillmentType.DELIVERY,
            status=OrderStatus.CREATED,
            branch_id=branch_id,
        )
        db.session.add(order)
        for item in cart.items:
            order_item = OrderItem(
                id=uuid4(),
                order_id=order.id,
                product_id=item.product_id,
                name=item.product.name,
                sku=item.product.sku,
                unit_price=item.unit_price,
                quantity=item.quantity,
            )
            db.session.add(order_item)
        return order

    @staticmethod
    def add_fulfillment_details(order: Order, payload: CheckoutConfirmRequest, branch_id: UUID) -> None:
        if payload.fulfillment_type == FulfillmentType.DELIVERY:
            delivery = OrderDeliveryDetails(
                id=uuid4(),
                order_id=order.id,
                delivery_slot_id=payload.delivery_slot_id,
                address=payload.address or "",
                slot_start=None,
                slot_end=None,
            )
            db.session.add(delivery)
            return
        now = datetime.utcnow()
        pickup = OrderPickupDetails(
            id=uuid4(),
            order_id=order.id,
            branch_id=branch_id,
            pickup_window_start=now,
            pickup_window_end=now,
        )
        db.session.add(pickup)

    @staticmethod
    def audit_creation(order: Order, total_amount: Decimal) -> None:
        AuditService.log_event(
            entity_type="order",
            action="CREATE",
            entity_id=order.id,
            actor_user_id=order.user_id,
            new_value={"order_number": order.order_number, "total_amount": float(total_amount)},
        )
