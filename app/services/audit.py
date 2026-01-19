"""Audit writing utilities."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from ..extensions import db
from ..models import Audit


class AuditService:
    @staticmethod
    def log_event(
        *,
        entity_type: str,
        action: str,
        actor_user_id: UUID | None = None,
        entity_id: UUID | None = None,
        old_value: dict[str, object] | None = None,
        new_value: dict[str, object] | None = None,
        context: dict[str, object] | None = None,
    ) -> Audit:
        session: Session = db.session
        entry = Audit(
            id=uuid4(),
            entity_type=entity_type,
            action=action,
            actor_user_id=actor_user_id,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            context=context,
            created_at=datetime.utcnow(),
        )
        session.add(entry)
        session.flush()
        return entry
