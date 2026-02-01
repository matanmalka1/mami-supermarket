"""Cart helper functions."""

from __future__ import annotations
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ...extensions import db
from ...models import Cart
from ...schemas.cart import CartItemResponse, CartResponse

def get_or_create_cart(user_id: int) -> Cart:
    """Get existing cart or create new one for user."""
    cart = db.session.query(Cart).options(
        selectinload(Cart.items)
    ).filter_by(user_id=user_id).first()
    
    if cart is None:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    
    return cart

def reload_cart(cart_id: int) -> Cart:
    """Reload cart with items from database."""
    return db.session.execute(
        select(Cart).where(Cart.id == cart_id).options(selectinload(Cart.items))
    ).scalar_one()

def to_response(cart: Cart) -> CartResponse:
    """Convert cart model to response schema."""
    items = [
        CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=Decimal(item.unit_price),
            product_name=item.product.name if item.product else None,
            product_image=item.product.image_url if item.product else None,
        )
        for item in cart.items
    ]
    total = sum(item.unit_price * item.quantity for item in items)
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        total_amount=total,
        items=items,
    )
