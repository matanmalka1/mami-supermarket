


# Deprecated: All seeding logic is now handled by scripts/seed.py and scripts/seed/ modules.
# This file is no longer used and can be deleted or ignored.

products: list[Product] = []
for cat_name, items in CATALOG.items():
    category = _get_or_create(
        session, Category,
        defaults={
            "description": f"{cat_name} items rich in flavor.",
            "icon_slug": f"icon-{cat_name.lower()}",
            "is_active": True,
        },
        name=cat_name
    )
    for idx, (name, sku, price, desc) in enumerate(items):
        is_organic = (idx % 2 == 0)
        old_price = price + 2 if idx % 3 == 0 else None
        unit = "kg" if "Bananas" in name or "Tomatoes" in name else ("pack" if "Yogurt" in name else "unit")
        nutritional_info = {"calories": 50 + idx * 10, "protein": 2 + idx} if idx % 2 == 0 else None
        products.append(_get_or_create(
            session, Product,
            defaults={
                "price": price,
                "old_price": old_price,
                "unit": unit,
                "nutritional_info": nutritional_info,
                "is_organic": is_organic,
                "description": desc,
                "category_id": category.id,
                "bin_location": f"A-{idx+1:02d}",
                "image_url": f"https://img.example.com/{sku}.jpg",
                "is_active": True,
            },
            sku=sku, name=name
        ))
