# seed/seed_orders.py
from __future__ import annotations

import datetime as dt
import random
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.address import Address
from app.models.branch import Branch
from app.models.delivery_slot import DeliverySlot
from app.models.enums import FulfillmentType, OrderStatus, PickedStatus, Role
from app.models.order import Order, OrderDeliveryDetails, OrderItem, OrderPickupDetails
from app.models.product import Product
from app.models.user import User

from scripts.seed.seed_orders_helpers import next_slot_window, sum_lines


def _order_no(user_id: int, seq: int) -> str:
    return f"ORD-{user_id:05d}-{seq:04d}"


def seed_orders(session: Session, *, max_orders_per_customer: int = 3) -> list[Order]:
    users = session.execute(select(User)).scalars().all()
    products = session.execute(select(Product)).scalars().all()
    branches = session.execute(select(Branch)).scalars().all()
    slots = session.execute(select(DeliverySlot)).scalars().all()
    addresses = session.execute(select(Address)).scalars().all()

    if not (users and products and branches and slots):
        raise RuntimeError("Missing base data. Seed branches/categories/products/users/slots first.")

    addrs_by_user: dict[int, list[Address]] = {}
    for a in addresses:
        addrs_by_user.setdefault(a.user_id, []).append(a)

    rnd = random.Random(2026)
    now = dt.datetime.utcnow()

    customers = [u for u in users if getattr(u, "role", None) == Role.CUSTOMER]
    target_users = customers or users

    created: list[Order] = []
    seq = 1

    for u in target_users:
        for _ in range(rnd.randint(1, max_orders_per_customer)):
            order_number = _order_no(u.id, seq); seq += 1
            existing = session.execute(select(Order).where(Order.order_number == order_number)).scalar_one_or_none()
            if existing:
                created.append(existing); continue

            fulfillment = rnd.choice([FulfillmentType.DELIVERY, FulfillmentType.PICKUP])
            status = rnd.choices(
                [OrderStatus.CREATED, OrderStatus.IN_PROGRESS, OrderStatus.READY, OrderStatus.OUT_FOR_DELIVERY, OrderStatus.DELIVERED, OrderStatus.CANCELED],
                weights=[0.10, 0.25, 0.20, 0.15, 0.25, 0.05],
                k=1,
            )[0]
            branch_id = getattr(u, "default_branch_id", None) or rnd.choice(branches).id

            order = Order(order_number=order_number, user_id=u.id, fulfillment_type=fulfillment, status=status, branch_id=branch_id, total_amount=Decimal("0.00"))
            session.add(order); session.flush()

            chosen = rnd.sample(products, k=min(rnd.randint(2, 7), len(products)))
            lines: list[tuple[Decimal, int]] = []
            for p in chosen:
                qty = rnd.randint(1, 4)
                unit_price = Decimal(str(p.price))
                picked = PickedStatus.PICKED if status in {OrderStatus.DELIVERED, OrderStatus.READY, OrderStatus.OUT_FOR_DELIVERY} else PickedStatus.PENDING
                if rnd.random() < 0.05:
                    picked = PickedStatus.MISSING
                session.add(OrderItem(order_id=order.id, product_id=p.id, name=p.name, sku=p.sku, unit_price=unit_price, quantity=qty, picked_status=picked))
                lines.append((unit_price, qty))

            order.total_amount = sum_lines(lines)
            session.add(order)

            if fulfillment == FulfillmentType.DELIVERY:
                branch_slots = [s for s in slots if s.branch_id == branch_id and getattr(s, "is_active", True)]
                slot = rnd.choice(branch_slots or slots)
                start, end = next_slot_window(slot, now=now)
                ua = rnd.choice(addrs_by_user.get(u.id, []) or [Address(user_id=u.id, address_line="Dizengoff 1", city="Tel Aviv-Yafo", country="Israel", postal_code="0000000")])
                addr_str = f"{ua.address_line}, {ua.city}, {ua.country}, {ua.postal_code}"
                session.add(OrderDeliveryDetails(order_id=order.id, delivery_slot_id=slot.id, address=addr_str, slot_start=start, slot_end=end))
            else:
                start = (now + dt.timedelta(hours=4)).replace(minute=0, second=0, microsecond=0)
                end = start + dt.timedelta(hours=2)
                session.add(OrderPickupDetails(order_id=order.id, branch_id=branch_id, pickup_window_start=start, pickup_window_end=end))

            created.append(order)

    session.flush()
    return created