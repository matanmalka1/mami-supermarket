from __future__ import annotations
import uuid
from sqlalchemy import Column, ForeignKey, Index, Numeric, String, Text
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, SoftDeleteMixin, TimestampMixin

class Product(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_name", "name"),
        Index("ix_products_category_id", "category_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False)
    sku = Column(String(64), nullable=False, unique=True, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    old_price = Column(Numeric(12, 2), nullable=True)
    unit = Column(String(24), nullable=True)
    nutritional_info = Column(sa.JSON, nullable=True)
    is_organic = Column(sa.Boolean, nullable=False, server_default='false')
    description = Column(Text, nullable=True)
    bin_location = Column(String(64), nullable=True)
    image_url = Column(String(256), nullable=True)

    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
