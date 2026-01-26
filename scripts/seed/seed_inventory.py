# scripts/seed/seed_inventory.py
from __future__ import annotations

import random
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.category import Category
from app.models.branch import Branch


def _ensure_inventory(
    session: Session,
    *,
    product_id: int,
    branch_id: int,
    available_quantity: int,
    reserved_quantity: int,
) -> Inventory:
    inv = session.execute(
        select(Inventory).where(
            Inventory.product_id == product_id,
            Inventory.branch_id == branch_id,
        )
    ).scalar_one_or_none()

    if inv:
        inv.available_quantity = available_quantity
        inv.reserved_quantity = reserved_quantity
        session.add(inv)
        return inv

    inv = Inventory(
        product_id=product_id,
        branch_id=branch_id,
        available_quantity=available_quantity,
        reserved_quantity=reserved_quantity,
    )
    session.add(inv)
    return inv


def _qty_range_for_category(category_name: str) -> tuple[int, int]:
    c = (category_name or "").lower()
    if "frozen" in c:
        return (5, 60)
    if ("dairy" in c) or ("eggs" in c):
        return (10, 120)
    if ("meat" in c) or ("fish" in c):
        return (3, 45)
    if ("fruits" in c) or ("vegetables" in c):
        return (15, 220)
    if "bakery" in c:
        return (8, 140)
    if "beverages" in c:
        return (20, 260)
    if "household" in c:
        return (10, 200)
    if "personal care" in c:
        return (6, 120)
    return (10, 180)


def seed_inventory(session: Session) -> list[Inventory]:
    branches = session.execute(select(Branch)).scalars().all()
    products = session.execute(select(Product)).scalars().all()
    categories = session.execute(select(Category)).scalars().all()

    if not branches:
        raise RuntimeError("No branches found. Seed branches first.")
    if not products:
        raise RuntimeError("No products found. Seed products first.")

    cat_by_id = {c.id: c.name for c in categories}
    rnd = random.Random(42)

    created: list[Inventory] = []
    for b in branches:
        branch_bias = 0.9 + (0.05 * (b.id % 5))
        for p in products:
            cat_name = cat_by_id.get(p.category_id, "Unknown")
            lo, hi = _qty_range_for_category(cat_name)
            available = int(rnd.randint(lo, hi) * branch_bias)
            reserved = rnd.randint(0, min(10, max(0, available // 10)))
            created.append(
                _ensure_inventory(
                    session,
                    product_id=p.id,
                    branch_id=b.id,
                    available_quantity=available,
                    reserved_quantity=reserved,
                )
            )

    session.flush()
    return created