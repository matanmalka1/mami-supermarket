from app.extensions import db
from app.models import Order, OrderItem
from app.middleware.error_handler import DomainError
from app.services.audit_service import AuditService

class OpsActionsService:
    @staticmethod
    def report_damage(order_id: int, item_id: int, payload, user_id: int):
        order = db.session.get(Order, order_id)
        if not order:
            raise DomainError("NOT_FOUND", "Order not found", status_code=404)
        item = (
            db.session.query(OrderItem)
            .filter_by(id=item_id, order_id=order_id)
            .first()
        )
        if not item:
            raise DomainError("NOT_FOUND", "Order item not found", status_code=404)
        AuditService.log_event(
            entity_type="order_item",
            action="REPORT_DAMAGE",
            actor_user_id=user_id,
            entity_id=item_id,
            new_value={
                "reason": payload.reason,
                "notes": payload.notes,
            },
        )
        return {"reported": True}