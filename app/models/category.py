from __future__ import annotations
import uuid
from sqlalchemy import Column, String, Text
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, SoftDeleteMixin, TimestampMixin

class Category(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon_slug = Column(String(64), nullable=True)
    is_active = Column(sa.Boolean, nullable=False, server_default='true')

    products = relationship("Product", back_populates="category")
