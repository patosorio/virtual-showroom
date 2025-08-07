"""
Authentication Service

Business logic for user authentication and management.
"""

from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import UserRepository
from app.services.base import BaseService
from app.core.exceptions import ValidationError, NotFoundError, ConflictError
from app.schemas.auth import (
    UserCreate, UserUpdate, UserResponse,
    UserProfileUpdate, UserRoleUpdate
)


class AuthService(BaseService[User, UserRepository]):
    """
    Authentication and user management service.
    """

    def __init__(self, db: AsyncSession):
        """Initialize auth service."""
        super().__init__(db, UserRepository, User)

    async def create_user(
        self,
        data: UserCreate,
        user_id: Optional[UUID] = None
    ) -> User:
        """
        Create a new user account.
        
        Args:
            data: User creation data
            user_id: ID of creating user (for admin operations)
            
        Returns:
            Created user
        """
        # Check if user already exists
        existing_user = await self.repository.get_by_email(data.email)
        if existing_user:
            raise ConflictError(
                detail=f"User with email {data.email} already exists",
                error_code="USER_ALREADY_EXISTS"
            )
        
        # Check Firebase UID uniqueness
        existing_firebase_user = await self.repository.get_by_firebase_uid(data.firebase_uid)
        if existing_firebase_user:
            raise ConflictError(
                detail="Firebase UID already associated with another account",
                error_code="FIREBASE_UID_EXISTS"
            )
        
        # Process user data
        user_data = data.model_dump()
        user_data['email'] = user_data['email'].lower()
        
        # Create user
        user = await self.repository.create(user_data, user_id)
        
        return user

    async def get_user_by_email(self, email: str) -> User:
        """
        Get user by email address.
        
        Args:
            email: User email
            
        Returns:
            User
        """
        user = await self.repository.get_by_email(email)
        if not user:
            raise NotFoundError(
                detail=f"User with email {email} not found",
                error_code="USER_NOT_FOUND"
            )
        return user

    async def get_user_by_firebase_uid(self, firebase_uid: str) -> User:
        """
        Get user by Firebase UID.
        
        Args:
            firebase_uid: Firebase user ID
            
        Returns:
            User
        """
        user = await self.repository.get_by_firebase_uid(firebase_uid)
        if not user:
            raise NotFoundError(
                detail=f"User with Firebase UID {firebase_uid} not found",
                error_code="USER_NOT_FOUND"
            )
        return user

    async def update_user_profile(
        self,
        user_id: UUID,
        data: UserProfileUpdate,
        current_user_id: Optional[UUID] = None
    ) -> User:
        """
        Update user profile information.
        
        Args:
            user_id: User UUID
            data: Profile update data
            current_user_id: ID of user making the update
            
        Returns:
            Updated user
        """
        # Check permissions - users can only update their own profile
        if current_user_id and current_user_id != user_id:
            # This would check if current user is admin
            pass
        
        update_data = data.model_dump(exclude_unset=True)
        
        updated_user = await self.repository.update(user_id, update_data, current_user_id)
        if not updated_user:
            raise NotFoundError(
                detail=f"User with ID {user_id} not found",
                error_code="USER_NOT_FOUND"
            )
        
        return updated_user

    async def update_user_role(
        self,
        user_id: UUID,
        role_data: UserRoleUpdate,
        admin_user_id: UUID
    ) -> User:
        """
        Update user role (admin only).
        
        Args:
            user_id: User UUID
            role_data: Role update data
            admin_user_id: ID of admin performing update
            
        Returns:
            Updated user
        """
        # Validate admin permissions
        admin_user = await self.repository.get_by_id(admin_user_id)
        if not admin_user or admin_user.role != "admin":
            raise ValidationError(
                detail="Only administrators can update user roles",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        # Update role
        update_data = {"role": role_data.role}
        
        updated_user = await self.repository.update(user_id, update_data, admin_user_id)
        if not updated_user:
            raise NotFoundError(
                detail=f"User with ID {user_id} not found",
                error_code="USER_NOT_FOUND"
            )
        
        return updated_user

    async def record_login(self, user_id: UUID) -> bool:
        """
        Record user login activity.
        
        Args:
            user_id: User UUID
            
        Returns:
            True if recorded successfully
        """
        return await self.repository.update_last_login(user_id)

    async def deactivate_user(
        self,
        user_id: UUID,
        admin_user_id: UUID
    ) -> User:
        """
        Deactivate a user account.
        
        Args:
            user_id: User UUID
            admin_user_id: ID of admin performing deactivation
            
        Returns:
            Deactivated user
        """
        update_data = {"is_active": False}
        
        updated_user = await self.repository.update(user_id, update_data, admin_user_id)
        if not updated_user:
            raise NotFoundError(
                detail=f"User with ID {user_id} not found",
                error_code="USER_NOT_FOUND"
            )
        
        return updated_user

    async def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get user statistics for admin dashboard.
        
        Returns:
            User statistics
        """
        return await self.repository.get_user_statistics()
