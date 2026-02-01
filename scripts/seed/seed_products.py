# seed/seed_products.py
from __future__ import annotations

import random
import re
from decimal import Decimal
from urllib.parse import quote

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:32] or "item"


def _img(text: str) -> str:
    return f"https://placehold.co/600x600?text={quote(text)}"


def _ensure_product(session: Session, *, sku: str, **fields) -> Product:
    p = session.execute(select(Product).where(Product.sku == sku)).scalar_one_or_none()
    if p:
        updated = False
        for k, v in fields.items():
            if getattr(p, k, None) != v:
                setattr(p, k, v); updated = True
        if hasattr(p, "is_active") and p.is_active is False:
            p.is_active = True; updated = True
        if updated:
            session.add(p)
        return p
    p = Product(sku=sku, **fields); session.add(p); return p


def seed_products(session: Session, *, target_count: int = 180) -> list[Product]:
    cats = session.execute(select(Category)).scalars().all()
    by_name = {c.name: c for c in cats}
    if not by_name:
        raise RuntimeError("No categories found. Seed categories first.")
    rnd = random.Random(42)

    groups: list[tuple[str, list[tuple[str, str, float, str]]]] = [
    ("Fruits & Vegetables", [
        ("Apples Gala","kg",12.9,"Fresh Gala apples."),
        ("Apples Granny Smith","kg",13.9,"Green sour apples."),
        ("Bananas","kg",9.9,"Ripe bananas."),
        ("Oranges","kg",8.9,"Juicy oranges."),
        ("Mandarins","kg",10.9,"Sweet mandarins."),
        ("Tomatoes","kg",9.9,"Fresh tomatoes."),
        ("Cherry Tomatoes","500g",7.9,"Cherry tomatoes."),
        ("Cucumbers","kg",8.5,"Fresh cucumbers."),
        ("Bell Pepper Red","kg",14.9,"Red bell pepper."),
        ("Bell Pepper Yellow","kg",14.9,"Yellow bell pepper."),
        ("Sweet Potatoes","kg",11.9,"Sweet potatoes."),
        ("Potatoes","kg",6.9,"White potatoes."),
        ("Carrots","kg",6.5,"Fresh carrots."),
        ("Zucchini","kg",7.9,"Zucchini."),
        ("Eggplant","kg",8.9,"Eggplant."),
        ("Avocado","unit",6.9,"Hass avocado."),
        ("Lemons","kg",10.9,"Juicy lemons."),
        ("Iceberg Lettuce","unit",6.9,"Iceberg lettuce."),
        ("Romaine Lettuce","unit",7.9,"Romaine lettuce."),
        ("Parsley","bunch",4.9,"Fresh parsley."),
        ("Cilantro","bunch",4.9,"Fresh cilantro."),
        ("Mint","bunch",4.9,"Fresh mint."),
    ]),

    ("Dairy & Eggs", [
        ("Milk 3%","1L",6.2,"Milk 3% (1L)."),
        ("Milk 1%","1L",6.0,"Milk 1% (1L)."),
        ("Chocolate Milk","1L",6.9,"Chocolate milk."),
        ("Greek Yogurt","200g",4.9,"Greek yogurt."),
        ("Natural Yogurt","200g",3.9,"Plain yogurt."),
        ("Cottage Cheese 5%","250g",7.9,"Cottage cheese 5%."),
        ("Cream Cheese","200g",8.9,"Cream cheese."),
        ("Yellow Cheese Slices","200g",12.9,"Sliced yellow cheese."),
        ("Mozzarella Cheese","200g",11.9,"Mozzarella cheese."),
        ("Butter","200g",10.9,"Butter (200g)."),
        ("Whipping Cream","250ml",7.9,"Whipping cream."),
        ("Eggs L","12pcs",14.9,"Large eggs 12 pack."),
        ("Eggs M","12pcs",13.9,"Medium eggs 12 pack."),
    ]),

    ("Meat & Fish", [
        ("Chicken Breast","kg",39.9,"Fresh chicken breast."),
        ("Chicken Thighs","kg",34.9,"Chicken thighs."),
        ("Whole Chicken","kg",22.9,"Whole chicken."),
        ("Ground Beef","kg",59.9,"Fresh ground beef."),
        ("Beef Entrecote","kg",89.9,"Entrecote steak."),
        ("Beef Stew Meat","kg",69.9,"Beef for stew."),
        ("Turkey Breast","kg",44.9,"Turkey breast."),
        ("Turkey Shawarma","kg",52.0,"Turkey shawarma."),
        ("Salmon Fillet","kg",99.0,"Fresh salmon fillet."),
        ("Tilapia Fillet","kg",64.9,"Tilapia fillet."),
        ("Frozen Fish Fingers","400g",19.9,"Fish fingers."),
    ]),

    ("Bakery", [
        ("White Bread","750g",9.5,"White bread."),
        ("Whole Wheat Bread","750g",10.5,"Whole wheat bread."),
        ("Sourdough Bread","700g",12.9,"Sourdough bread."),
        ("Pita Bread","10pcs",8.9,"Pita bread 10 pack."),
        ("Challah","unit",14.9,"Challah."),
        ("Bagel","unit",4.9,"Fresh bagel."),
        ("Croissant","unit",6.9,"Croissant."),
        ("Chocolate Croissant","unit",7.9,"Chocolate croissant."),
    ]),

    ("Frozen", [
        ("Frozen Peas","800g",9.9,"Frozen peas."),
        ("Frozen Corn","800g",9.9,"Frozen corn."),
        ("Frozen Fries","1kg",14.9,"Frozen fries."),
        ("Frozen Pizza","unit",19.9,"Frozen pizza."),
        ("Frozen Lasagna","unit",24.9,"Frozen lasagna."),
        ("Ice Cream Vanilla","1L",24.9,"Vanilla ice cream."),
        ("Ice Cream Chocolate","1L",24.9,"Chocolate ice cream."),
    ]),

    ("Beverages", [
        ("Mineral Water","1.5L",4.5,"Mineral water."),
        ("Sparkling Water","1.5L",4.9,"Sparkling water."),
        ("Cola","1.5L",8.9,"Cola."),
        ("Diet Cola","1.5L",8.9,"Diet cola."),
        ("Orange Juice","1L",11.9,"Orange juice."),
        ("Apple Juice","1L",11.9,"Apple juice."),
        ("Iced Tea Lemon","1.5L",10.9,"Iced tea."),
        ("Energy Drink","250ml",7.9,"Energy drink."),
    ]),

    ("Snacks", [
        ("Potato Chips Classic","70g",6.5,"Potato chips."),
        ("Potato Chips BBQ","70g",6.5,"BBQ chips."),
        ("Salted Peanuts","200g",9.9,"Peanuts."),
        ("Cashews Roasted","200g",18.9,"Cashews."),
        ("Almonds Roasted","200g",18.9,"Almonds."),
        ("Protein Bar","unit",8.9,"Protein bar."),
        ("Granola Bar","unit",4.9,"Granola bar."),
    ]),

    ("Pantry", [
        ("Pasta Spaghetti","500g",6.9,"Spaghetti."),
        ("Pasta Penne","500g",6.9,"Penne pasta."),
        ("Rice White","1kg",8.9,"White rice."),
        ("Rice Basmati","1kg",11.9,"Basmati rice."),
        ("Tuna Can","160g",7.5,"Tuna can."),
        ("Canned Corn","340g",6.9,"Sweet corn."),
        ("Chickpeas Can","560g",7.9,"Chickpeas."),
        ("Tomato Sauce","500g",5.9,"Tomato sauce."),
        ("Ketchup","500g",9.9,"Ketchup."),
        ("Mayonnaise","500g",9.9,"Mayonnaise."),
        ("Olive Oil","1L",42.9,"Olive oil."),
        ("Sugar","1kg",6.9,"Sugar."),
        ("Salt","1kg",4.5,"Salt."),
    ]),

    ("Breakfast", [
        ("Corn Flakes","500g",14.9,"Corn flakes."),
        ("Chocolate Cereal","500g",16.9,"Chocolate cereal."),
        ("Oat Flakes","500g",9.9,"Oats."),
        ("Chocolate Spread","400g",17.9,"Chocolate spread."),
        ("Peanut Butter","340g",14.9,"Peanut butter."),
        ("Honey","350g",24.9,"Honey."),
        ("Strawberry Jam","340g",12.9,"Jam."),
    ]),

    ("Household", [
        ("Toilet Paper","12 rolls",29.9,"Toilet paper."),
        ("Paper Towels","6 rolls",22.9,"Paper towels."),
        ("Dish Soap","750ml",12.9,"Dish soap."),
        ("Laundry Detergent","2L",34.9,"Detergent."),
        ("Fabric Softener","2L",18.9,"Fabric softener."),
        ("All Purpose Cleaner","1L",9.9,"Cleaning spray."),
    ]),

    ("Personal Care", [
        ("Shampoo","500ml",19.9,"Shampoo."),
        ("Conditioner","500ml",19.9,"Conditioner."),
        ("Body Wash","700ml",18.9,"Body wash."),
        ("Hand Soap","500ml",7.9,"Hand soap."),
        ("Soap Bars","4pcs",9.9,"Soap bars."),
        ("Toothpaste","unit",12.9,"Toothpaste."),
        ("Deodorant","unit",16.9,"Deodorant."),
    ]),
]

    created: list[Product] = []
    i = 0
    mult = max(1, target_count // 120)
    for cat_name, items in groups:
        c = by_name.get(cat_name)
        if not c:
            continue
        aisle = (_slug(cat_name)[:1].upper() or "A")
        for base_name, unit, base_price, desc in items:
            for v in range(1, mult + 1):
                i += 1
                name = base_name if v == 1 else f"{base_name} - Value Pack {v}"
                price = Decimal(str(base_price)) + Decimal(str(rnd.choice([0,0.5,1.0,1.5])))
                old_price = (price + Decimal("2.00")) if rnd.random() < 0.25 else None
                is_org = (cat_name == "Fruits & Vegetables" and rnd.random() < 0.2)
                nutrition = None
                if cat_name in {"Beverages","Snacks","Pantry","Breakfast"} and rnd.random() < 0.8:
                    nutrition = {"calories": int(80 + rnd.random()*260), "protein_g": round(rnd.random()*12, 1)}
                sku = f"{aisle}-{_slug(base_name)[:16].upper()}-{v:02d}"
                created.append(_ensure_product(
                    session, sku=sku, name=name, category_id=c.id, price=price, old_price=old_price,
                    unit=unit, nutritional_info=nutrition, is_organic=is_org, description=desc,
                    bin_location=f"{aisle}-{i:03d}", image_url=_img(name),
                ))
                if len(created) >= target_count:
                    session.flush(); return created

    session.flush()
    return created