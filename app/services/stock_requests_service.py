"""Stock request workflows for employees and managers/admins."""

from __future__ import annotations
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Inventory, StockRequest
from app.models.enums import StockRequestStatus, StockRequestType
from app.schemas.stock_requests import BulkReviewRequest, StockRequestCreateRequest, StockRequestResponse
from app.services.audit_service import AuditService

class StockRequestService:
    @staticmethod
    def create_request(user_id: UUID, payload: StockRequestCreateRequest) -> StockRequestResponse:
        inventory = db.session.execute(
            sa.select(Inventory)
            .where(Inventory.branch_id == payload.branch_id)
            .where(Inventory.product_id == payload.product_id)
        ).scalar_one_or_none()
        if not inventory:
            raise DomainError("NOT_FOUND", "Inventory row not found for branch/product", status_code=404)
        request = StockRequest(
            id=uuid4(),
            branch_id=payload.branch_id,
            product_id=payload.product_id,
            quantity=payload.quantity,
            request_type=payload.request_type,
            status=StockRequestStatus.PENDING,
            actor_user_id=user_id,
        )
        db.session.add(request)
        db.session.commit()
        AuditService.log_event(
            entity_type="stock_request",
            action="CREATE",
            actor_user_id=user_id,
            entity_id=request.id,
            new_value={
                "branch_id": str(payload.branch_id),
                "product_id": str(payload.product_id),
                "quantity": payload.quantity,
                "request_type": payload.request_type.value,
            },
        )
        return StockRequestService._to_response(request)

    @staticmethod
    def list_my(user_id: UUID, limit: int, offset: int) -> tuple[list[StockRequestResponse], int]:
        stmt = (
            sa.select(StockRequest)
            .where(StockRequest.actor_user_id == user_id)
            .order_by(StockRequest.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        total = db.session.scalar(
            sa.select(sa.func.count()).select_from(StockRequest).where(StockRequest.actor_user_id == user_id)
        )
        rows = db.session.execute(stmt).scalars().all()
        return [StockRequestService._to_response(row) for row in rows], total or 0

    @staticmethod
    def list_admin(status: StockRequestStatus | None, limit: int, offset: int) -> tuple[list[StockRequestResponse], int]:
        stmt = sa.select(StockRequest).order_by(StockRequest.created_at.desc())
        if status:
            stmt = stmt.where(StockRequest.status == status)
        total = db.session.scalar(sa.select(sa.func.count()).select_from(stmt.subquery()))
        rows = db.session.execute(stmt.offset(offset).limit(limit)).scalars().all()
        return [StockRequestService._to_response(row) for row in rows], total or 0

    @staticmethod
    def review(
        request_id: UUID,
        status: StockRequestStatus,
        approved_quantity: int | None,
        rejection_reason: str | None,
        actor_id: UUID,
    ) -> StockRequestResponse:
        session = db.session
        stock_request = session.execute(
            sa.select(StockRequest)
            .where(StockRequest.id == request_id)
            .options(selectinload(StockRequest.branch), selectinload(StockRequest.product))
            .with_for_update()
        ).scalar_one_or_none()
        if not stock_request:
            raise DomainError("NOT_FOUND", "Stock request not found", status_code=404)
        if stock_request.status != StockRequestStatus.PENDING:
            raise DomainError("INVALID_STATUS", "Stock request already reviewed", status_code=409)

        if status == StockRequestStatus.APPROVED:
            if approved_quantity is None or approved_quantity <= 0:
                raise DomainError("INVALID_QUANTITY", "Approved quantity must be positive", status_code=400)
            StockRequestService._apply_inventory_change(
                stock_request.branch_id,
                stock_request.product_id,
                stock_request.request_type,
                approved_quantity,
                actor_id,
            )
            stock_request.quantity = approved_quantity
        elif status == StockRequestStatus.REJECTED:
            if not rejection_reason:
                raise DomainError("INVALID_REJECTION", "Rejection reason is required", status_code=400)
        stock_request.status = status
        session.add(stock_request)
        session.commit()
        AuditService.log_event(
            entity_type="stock_request",
            action="REVIEW",
            actor_user_id=actor_id,
            entity_id=stock_request.id,
            old_value={"status": StockRequestStatus.PENDING.value},
            new_value={"status": status.value, "approved_quantity": stock_request.quantity, "rejection_reason": rejection_reason},
        )
        return StockRequestService._to_response(stock_request)

    @staticmethod
    def bulk_review(payload: BulkReviewRequest, actor_id: UUID) -> list[dict]:
        results: list[dict] = []
        for item in payload.items:
            try:
                res = StockRequestService.review(
                    item.request_id,
                    item.status,
                    item.approved_quantity,
                    item.rejection_reason,
                    actor_id,
                )
                results.append({"request_id": item.request_id, "status": res.status, "result": "ok"})
            except DomainError as exc:
                results.append(
                    {
                        "request_id": item.request_id,
                        "status": None,
                        "result": "error",
                        "error_code": exc.code,
                        "message": exc.message,
                    }
                )
        return results

    @staticmethod
    def _apply_inventory_change(
        branch_id: UUID,
        product_id: UUID,
        request_type: StockRequestType,
        approved_quantity: int,
        actor_id: UUID,
    ) -> None:
        session = db.session
        inventory = session.execute(
            sa.select(Inventory)
            .where(Inventory.branch_id == branch_id)
            .where(Inventory.product_id == product_id)
            .with_for_update()
        ).scalar_one_or_none()
        if not inventory:
            raise DomainError("NOT_FOUND", "Inventory not found for branch/product", status_code=404)
        old_value = {
            "available_quantity": inventory.available_quantity,
            "reserved_quantity": inventory.reserved_quantity,
        }
        if request_type == StockRequestType.SET_QUANTITY:
            inventory.available_quantity = approved_quantity
        elif request_type == StockRequestType.ADD_QUANTITY:
            inventory.available_quantity += approved_quantity
        session.add(inventory)
        AuditService.log_event(
            entity_type="inventory",
            action="STOCK_REQUEST_APPLY",
            actor_user_id=actor_id,
            entity_id=inventory.id,
            old_value=old_value,
            new_value={
                "available_quantity": inventory.available_quantity,
                "reserved_quantity": inventory.reserved_quantity,
            },
        )

    @staticmethod
    def _to_response(row: StockRequest) -> StockRequestResponse:
        return StockRequestResponse(
            id=row.id,
            branch_id=row.branch_id,
            product_id=row.product_id,
            quantity=row.quantity,
            request_type=row.request_type,
            status=row.status,
            actor_user_id=row.actor_user_id,
            created_at=row.created_at,
        )
