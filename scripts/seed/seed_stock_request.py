# seed/seed_stock_request.py
from __future__ import annotations

import random
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import Role, StockRequestStatus, StockRequestType
from app.models.inventory import Inventory
from app.models.stock_request import StockRequest
from app.models.user import User


def seed_stock_requests(session: Session, *, limit: int = 30) -> list[StockRequest]:
    inv_rows = session.execute(select(Inventory)).scalars().all()
    users = session.execute(select(User)).scalars().all()
    if not inv_rows:
        raise RuntimeError("No inventory found. Seed inventory first.")
    if not users:
        raise RuntimeError("No users found. Seed users first.")

    rnd = random.Random(777)
    actors = [u for u in users if getattr(u, "role", None) in (Role.MANAGER, Role.ADMIN)]
    actor = actors[0] if actors else users[0]

    low = [r for r in inv_rows if r.available_quantity <= r.reorder_point]
    pool = low or inv_rows

    created: list[StockRequest] = []
    for r in rnd.sample(pool, k=min(limit, len(pool))):
        req_type = rnd.choice([StockRequestType.ADD_QUANTITY, StockRequestType.SET_QUANTITY])
        if req_type == StockRequestType.ADD_QUANTITY:
            qty = max(5, r.reorder_point * 2 - r.available_quantity + rnd.randint(0, 15))
        else:
            qty = max(0, r.reorder_point * 3 + rnd.randint(-10, 25))

        status = rnd.choices(
            [StockRequestStatus.PENDING, StockRequestStatus.APPROVED, StockRequestStatus.REJECTED],
            weights=[0.70, 0.25, 0.05],
            k=1,
        )[0]

        sr = StockRequest(
            branch_id=r.branch_id,
            product_id=r.product_id,
            quantity=qty,
            request_type=req_type,
            status=status,
            actor_user_id=actor.id,
        )
        session.add(sr)
        created.append(sr)

    session.flush()
    return created