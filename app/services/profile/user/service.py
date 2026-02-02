"""Profile management service."""

from __future__ import annotations
from ....extensions import db
from ....middleware.error_handler import DomainError
from ....models import User
from ....schemas.profile import (
    UpdatePhoneRequest,
    UpdateProfileRequest,
    UserProfileResponse,
)
from app.models.enums import MembershipTier
from app.services.shared_queries import SharedQueries, SharedOperations


class ProfileService:
    @staticmethod
    def get_user_profile(user_id: int) -> UserProfileResponse:
        """Get user profile information."""
        user = SharedQueries.get_active_user_by_id(user_id)
        return SharedQueries.user_to_profile_response(user)

    @staticmethod
    def update_phone(user_id: int, data: UpdatePhoneRequest) -> UserProfileResponse:
        """Update user phone number."""
        user = SharedQueries.get_active_user_by_id(user_id)
        old_phone = user.phone
        user.phone = data.phone
        
        SharedOperations.commit_with_audit(
            entity_type="user",
            action="UPDATE_PHONE",
            entity_id=user.id,
            actor_user_id=user_id,
            old_value={"phone": old_phone},
            new_value={"phone": data.phone},
            error_message="Could not update phone",
        )
        
        return ProfileService.get_user_profile(user_id)

    @staticmethod
    def update_profile(user_id: int, data: UpdateProfileRequest) -> UserProfileResponse:
        """Update user profile information."""
        user = SharedQueries.get_active_user_by_id(user_id)
        old_values = {}
        new_values = {}
        
        if data.full_name is not None:
            old_values["full_name"] = user.full_name
            user.full_name = data.full_name
            new_values["full_name"] = data.full_name
        
        if data.phone is not None:
            old_values["phone"] = user.phone
            user.phone = data.phone
            new_values["phone"] = data.phone
        
        if not new_values:
            return ProfileService.get_user_profile(user_id)
        
        SharedOperations.commit_with_audit(
            entity_type="user",
            action="UPDATE_PROFILE",
            entity_id=user.id,
            actor_user_id=user_id,
            old_value=old_values,
            new_value=new_values,
            error_message="Could not update profile",
        )
        
        return ProfileService.get_user_profile(user_id)

    @staticmethod
    def update_membership(user_id: int, tier: MembershipTier) -> MembershipTier:
        user = SharedQueries.get_active_user_by_id(user_id)

        old_tier = user.membership_tier
        user.membership_tier = tier.value

        SharedOperations.commit_with_audit(
            entity_type="user",
            action="UPDATE_MEMBERSHIP",
            entity_id=user.id,
            actor_user_id=user_id,
            old_value={"membership_tier": old_tier},
            new_value={"membership_tier": tier.value},
            error_message="Could not update membership",
        )

        return tier
