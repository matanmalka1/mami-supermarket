from __future__ import annotations
from datetime import datetime
from pydantic import Field

from .common import DefaultModel

class AuditQuery(DefaultModel):
    entity_type: str | None = Field(default=None, min_length=2, max_length=50)
    action: str | None = Field(default=None, min_length=2, max_length=50)
    actor_user_id: int | None = Field(default=None, gt=0)
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0, le=100000)

class AuditResponse(DefaultModel):
    id: int = Field(gt=0)
    entity_type: str = Field(min_length=2, max_length=50)
    entity_id: int = Field(gt=0)
    action: str = Field(min_length=2, max_length=50)
    old_value: dict[str, object] | None
    new_value: dict[str, object] | None
    context: dict[str, object] | None
    actor_user_id: int | None = Field(default=None, gt=0)
    created_at: datetime
