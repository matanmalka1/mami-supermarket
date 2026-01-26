# seed/seed_audit.py
from __future__ import annotations

import random
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit import Audit
from app.models.enums import Role
from app.models.product import Product
from app.models.stock_request import StockRequest
from app.models.user import User


def seed_audit(session: Session, *, limit: int = 60) -> list[Audit]:
    users = session.execute(select(User)).scalars().all()
    products = session.execute(select(Product)).scalars().all()
    stock = session.execute(select(StockRequest)).scalars().all()

    if not users:
        raise RuntimeError("Seed users first.")

    rnd = random.Random(909)
    actors = [u for u in users if getattr(u, "role", None) in (Role.ADMIN, Role.MANAGER)]
    actor = actors[0] if actors else users[0]

    created: list[Audit] = []

    for _ in range(limit):
        choice = rnd.choice(["product", "stock_request", "user"])
        if choice == "product" and products:
            p = rnd.choice(products)
            created.append(Audit(entity_type="product", entity_id=p.id, action=rnd.choice(["create", "update_price", "toggle_active"]), old_value=None, new_value={"sku": p.sku, "name": p.name}, context={"seed": True}, actor_user_id=actor.id))
        elif choice == "stock_request" and stock:
            sr = rnd.choice(stock)
            created.append(Audit(entity_type="stock_request", entity_id=sr.id, action="review", old_value={"status": "PENDING"}, new_value={"status": sr.status}, context={"seed": True}, actor_user_id=actor.id))
        else:
            u = rnd.choice(users)
            created.append(Audit(entity_type="user", entity_id=u.id, action="login", old_value=None, new_value={"email": u.email}, context={"seed": True}, actor_user_id=u.id))

    for a in created:
        session.add(a)

    session.flush()
    return created