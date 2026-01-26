# scripts/seed/seed.py
from __future__ import annotations

import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.models.product import Product
from app.models.category import Category

from scripts.seed.seed_branches import seed_branches
from scripts.seed.seed_categories import seed_categories
from scripts.seed.seed_products import seed_products
from scripts.seed.seed_inventory import seed_inventory
from scripts.seed.seed_users import seed_users
from scripts.seed.seed_address import seed_addresses
from scripts.seed.seed_delivery_slots import seed_delivery_slots
from scripts.seed.seed_carts import seed_carts
from scripts.seed.seed_orders import seed_orders
from scripts.seed.seed_payment_tokens import seed_payment_tokens
from scripts.seed.seed_stock_request import seed_stock_requests
from scripts.seed.seed_idempotency_keys import seed_idempotency_keys
from scripts.seed.seed_wishlist_items import seed_wishlist_items
from scripts.seed.seed_auth_tokens import seed_auth_tokens
from scripts.seed.seed_audit import seed_audit


def run_seed() -> None:
    db_url = os.getenv("DATABASE_URL", "postgresql://matan:Aa100100!!@localhost:5432/matan_db")
    engine = create_engine(db_url, echo=False)
    SessionLocal = sessionmaker(bind=engine)

    # Ensure all tables exist (requires app.models to import all model classes)
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        branches = seed_branches(session)
        print(f"Seeded branches: {len(branches)}")

        categories = seed_categories(session)
        print(f"Seeded categories: {len(categories)}")

        products = seed_products(session, target_count=180)
        print(f"Seeded products: {len(products)}")

        inv = seed_inventory(session)
        print(f"Seeded inventory rows: {len(inv)}")

        default_branch_id = branches[0].id if branches else None
        users = seed_users(session, default_branch_id=default_branch_id)
        print(f"Seeded users: {len(users)}")

        addrs = seed_addresses(session, [u.id for u in users])
        print(f"Seeded addresses: {len(addrs)}")

        slots = seed_delivery_slots(session)
        print(f"Seeded delivery slots: {len(slots)}")

        carts = seed_carts(session)
        print(f"Seeded carts: {len(carts)}")

        orders = seed_orders(session)
        print(f"Seeded orders: {len(orders)}")

        pts = seed_payment_tokens(session)
        print(f"Seeded payment tokens: {len(pts)}")

        srs = seed_stock_requests(session)
        print(f"Seeded stock requests: {len(srs)}")

        idems = seed_idempotency_keys(session)
        print(f"Seeded idempotency keys: {len(idems)}")

        wish = seed_wishlist_items(session)
        print(f"Seeded wishlist items: {len(wish)}")

        otps, resets = seed_auth_tokens(session)
        print(f"Seeded OTPs: {len(otps)} | password reset tokens: {len(resets)}")

        audits = seed_audit(session)
        print(f"Seeded audit rows: {len(audits)}")

        _verify_seed_data(session)
        session.commit()
        print("✅ Seeding complete!")


def _verify_seed_data(session) -> None:
    missing_icons = session.execute(select(Category).where(Category.icon_slug.is_(None))).scalars().all()
    if missing_icons:
        raise RuntimeError(f"Categories missing icon_slug: {[c.name for c in missing_icons]}")

    missing_products = session.execute(
        select(Product).where(
            Product.image_url.is_(None)
            | Product.bin_location.is_(None)
            | Product.unit.is_(None)
        )
    ).scalars().all()
    if missing_products:
        raise RuntimeError(f"Products missing required display fields: {len(missing_products)} found")


if __name__ == "__main__":
    run_seed()