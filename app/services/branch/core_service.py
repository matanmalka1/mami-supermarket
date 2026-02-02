from __future__ import annotations
from sqlalchemy import func, select
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Branch
from app.schemas.branches import BranchResponse
from app.services.shared_queries import SharedOperations
from app.services.audit_service import AuditService


class BranchCoreService:
    @staticmethod
    def ensure_delivery_source_branch_exists(branch_id: str) -> Branch:
        """Ensure configured DELIVERY_SOURCE_BRANCH_ID exists; raise if not."""
        if not branch_id:
            raise DomainError(
                "CONFIG_ERROR",
                "DELIVERY_SOURCE_BRANCH_ID is not set",
                status_code=400,
            )
        try:
            branch_pk = int(branch_id)
        except ValueError as exc:
            raise DomainError(
                "CONFIG_ERROR",
                "DELIVERY_SOURCE_BRANCH_ID is not a valid branch ID",
                status_code=400,
            ) from exc

        branch = db.session.get(Branch, branch_pk)
        if not branch:
            raise DomainError(
                "CONFIG_ERROR",
                "Configured DELIVERY_SOURCE_BRANCH_ID does not exist in branches table",
                status_code=404,
            )
        return branch

    @staticmethod
    def list_branches(limit: int, offset: int) -> tuple[list[BranchResponse], int]:
        stmt = (
            select(Branch)
            .where(Branch.is_active.is_(True))
        )
        
        def transform(branch):
            return BranchResponse(id=branch.id, name=branch.name, address=branch.address, is_active=branch.is_active)
        
        branches, total = SharedOperations.paginate_query(
            base_query=stmt,
            model_class=Branch,
            limit=limit,
            offset=offset,
            transform_fn=transform,
        )
        return branches, total

    @staticmethod
    def create_branch(name: str, address: str) -> BranchResponse:
        branch = Branch(name=name, address=address)
        db.session.add(branch)
        db.session.commit()
        AuditService.log_event(entity_type="branch", action="CREATE", entity_id=branch.id)
        return BranchResponse(id=branch.id, name=branch.name, address=branch.address, is_active=branch.is_active)

    @staticmethod
    def update_branch(branch_id: int, name: str, address: str) -> BranchResponse:
        branch = db.session.get(Branch, branch_id)
        if not branch:
            raise DomainError("NOT_FOUND", "Branch not found", status_code=404)
        old_value = {"name": branch.name, "address": branch.address}
        branch.name = name
        branch.address = address

        db.session.add(branch)
        db.session.commit()
        AuditService.log_event(
            entity_type="branch",
            action="UPDATE",
            entity_id=branch.id,
            old_value=old_value,
            new_value={"name": name, "address": address},
        )
        return BranchResponse(id=branch.id, name=branch.name, address=branch.address, is_active=branch.is_active)

    @staticmethod
    def toggle_branch(branch_id: int, active: bool) -> BranchResponse:
        branch = db.session.get(Branch, branch_id)
        if not branch:
            raise DomainError("NOT_FOUND", "Branch not found", status_code=404)
        branch.is_active = active
        db.session.add(branch)
        db.session.commit()
        AuditService.log_event(
            entity_type="branch",
            action="DEACTIVATE" if not active else "ACTIVATE",
            entity_id=branch.id,
            new_value={"is_active": active},
        )
        return BranchResponse(id=branch.id, name=branch.name, address=branch.address, is_active=branch.is_active)
