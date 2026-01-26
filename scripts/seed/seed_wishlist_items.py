# seed/seed_wishlist_items.py
from __future__ import annotations

import random
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import Role
from app.models.product import Product
from app.models.user import User
from app.models.wishlist_item import WishlistItem


def seed_wishlist_items(session: Session, *, limit_per_user: int = 6) -> list[WishlistItem]:
    users = session.execute(select(User)).scalars().all()
    products = session.execute(select(Product)).scalars().all()
    if not users or not products:
        raise RuntimeError("Seed users and products first.")

    rnd = random.Random(555)
    customers = [u for u in users if getattr(u, "role", None) == Role.CUSTOMER] or users

    created: list[WishlistItem] = []
    for u in customers:
        k = min(limit_per_user, len(products))
        for p in rnd.sample(products, k=rnd.randint(1, k)):
            existing = session.execute(
                select(WishlistItem).where(WishlistItem.user_id == u.id, WishlistItem.product_id == p.id)
            ).scalar_one_or_none()
            if existing:
                continue
            wi = WishlistItem(
                user_id=u.id,
                product_id=p.id,
                note=rnd.choice([None, "Buy on discount", "For weekend", "Family favorite"]),
                priority=rnd.randint(1, 5),
            )
            session.add(wi)
            created.append(wi)

    session.flush()
    return created