# seed/seed_carts.py
from __future__ import annotations

import random
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cart import Cart, CartItem
from app.models.enums import CartStatus, Role
from app.models.product import Product
from app.models.user import User


def _get_or_create_cart(session: Session, *, user_id: int, status: CartStatus) -> Cart:
    c = session.execute(select(Cart).where(Cart.user_id == user_id, Cart.status == status)).scalar_one_or_none()
    if c:
        return c
    c = Cart(user_id=user_id, status=status); session.add(c); session.flush(); return c


def _upsert_item(session: Session, *, cart_id: int, product_id: int, quantity: int, unit_price: str) -> CartItem:
    it = session.execute(select(CartItem).where(CartItem.cart_id == cart_id, CartItem.product_id == product_id)).scalar_one_or_none()
    if it:
        it.quantity = quantity; it.unit_price = unit_price; session.add(it); return it
    it = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity, unit_price=unit_price); session.add(it); return it


def seed_carts(session: Session, *, max_items_per_cart: int = 6) -> list[Cart]:
    users = session.execute(select(User)).scalars().all()
    products = session.execute(select(Product)).scalars().all()
    if not users:
        raise RuntimeError("No users found. Seed users first.")
    if not products:
        raise RuntimeError("No products found. Seed products first.")

    rnd = random.Random(123)
    customers = [u for u in users if getattr(u, "role", None) == Role.CUSTOMER]
    target = customers or users

    created: list[Cart] = []
    for u in target:
        # ACTIVE cart
        active = _get_or_create_cart(session, user_id=u.id, status=CartStatus.ACTIVE)
        created.append(active)

        chosen = rnd.sample(products, k=min(rnd.randint(2, max_items_per_cart), len(products)))
        for p in chosen:
            _upsert_item(session, cart_id=active.id, product_id=p.id, quantity=rnd.randint(1, 4), unit_price=str(p.price))

        # ABANDONED cart for some users (helps ops/admin UI)
        if rnd.random() < 0.35:
            abandoned = _get_or_create_cart(session, user_id=u.id, status=CartStatus.ABANDONED)
            created.append(abandoned)
            chosen2 = rnd.sample(products, k=min(rnd.randint(1, 4), len(products)))
            for p in chosen2:
                price = Decimal(str(p.price)) + Decimal("0.00")
                _upsert_item(session, cart_id=abandoned.id, product_id=p.id, quantity=rnd.randint(1, 2), unit_price=str(price))

    session.flush()
    return created