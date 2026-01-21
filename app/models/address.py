from __future__ import annotations
import uuid
from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Address(Base, TimestampMixin):
    __tablename__ = "addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    address_line = Column(String(256), nullable=False)
    city = Column(String(64), nullable=False)
    country = Column(String(64), nullable=False)
    postal_code = Column(String(16), nullable=False)
    is_default = Column(Boolean, nullable=False, server_default="false")

    user = relationship("User", back_populates="addresses")
