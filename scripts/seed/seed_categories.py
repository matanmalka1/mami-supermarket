# seed/seed_categories.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


def _ensure_category(session: Session, *, name: str, description: str | None, icon_slug: str) -> Category:
    c = session.execute(select(Category).where(Category.name == name)).scalar_one_or_none()
    if c:
        updated = False
        if hasattr(c, "is_active") and c.is_active is False:
            c.is_active = True; updated = True
        if c.description != description:
            c.description = description; updated = True
        if getattr(c, "icon_slug", None) != icon_slug:
            c.icon_slug = icon_slug; updated = True
        if updated:
            session.add(c)
        return c
    c = Category(name=name, description=description, icon_slug=icon_slug); session.add(c); return c


def seed_categories(session: Session) -> list[Category]:
    data = [
        ("Fruits & Vegetables", "Fresh produce: fruits, vegetables, herbs.", "produce"),
        ("Dairy & Eggs", "Milk, yogurt, cheese, eggs, butter.", "dairy"),
        ("Meat & Fish", "Fresh meat, poultry, fish, deli meats.", "meat"),
        ("Bakery", "Bread, rolls, pastries, cakes.", "bakery"),
        ("Frozen", "Frozen vegetables, ice cream, frozen meals.", "frozen"),
        ("Beverages", "Water, soft drinks, juice, energy drinks.", "drinks"),
        ("Snacks", "Chips, crackers, nuts, bars.", "snacks"),
        ("Pantry", "Pasta, rice, canned food, sauces, spices.", "pantry"),
        ("Breakfast", "Cereal, spreads, jams, honey.", "breakfast"),
        ("Household", "Paper goods, cleaning supplies.", "household"),
        ("Personal Care", "Shampoo, soap, deodorant, skincare.", "personal_care"),
        ("Baby", "Diapers, wipes, baby food.", "baby"),
        ("Pets", "Pet food and pet care.", "pets"),
        ("Health", "OTC items and wellness basics.", "health"),
    ]
    created: list[Category] = []
    for name, desc, icon_slug in data:
        created.append(_ensure_category(session, name=name, description=desc, icon_slug=icon_slug))
    session.flush()
    return created