"""
User Repository

Data access layer for User entity.
Handles user authentication and management operations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    User repository for authentication and user management.
    """

    def __init__(self, db: AsyncSession):
        """Initialize with User model."""
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User email
            
        Returns:
            User or None if not found
        """
        return await self.get_by_field("email", email.lower())

    async def get_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """
        Get user by Firebase UID.
        
        Args:
            firebase_uid: Firebase user ID
            
        Returns:
            User or None if not found
        """
        return await self.get_by_field("firebase_uid", firebase_uid)

    async def check_email_exists(self, email: str, exclude_id: Optional[UUID] = None) -> bool:
        """
        Check if email already exists.
        
        Args:
            email: Email to check
            exclude_id: User ID to exclude from check (for updates)
            
        Returns:
            True if email exists, False otherwise
        """
        query = select(User).where(and_(
            User.email == email.lower(),
            User.is_deleted == False
        ))
        
        if exclude_id:
            query = query.where(User.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_active_users(
        self,
        skip: int = 0,
        limit: int = 50
    ) -> List[User]:
        """
        Get all active users.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of active users
        """
        query = (
            select(User)
            .where(and_(
                User.is_active == True,
                User.is_deleted == False
            ))
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_users_by_role(
        self,
        role: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[User]:
        """
        Get users by role.
        
        Args:
            role: User role
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of users with the specified role
        """
        query = (
            select(User)
            .where(and_(
                User.role == role,
                User.is_deleted == False
            ))
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def search_users(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[User]:
        """
        Search users by email or display name.
        
        Args:
            search_term: Text to search for
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of matching users
        """
        search_pattern = f"%{search_term}%"
        
        query = (
            select(User)
            .where(and_(
                User.is_deleted == False,
                or_(
                    User.email.ilike(search_pattern),
                    User.display_name.ilike(search_pattern)
                )
            ))
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_recently_active_users(
        self,
        days: int = 30,
        limit: int = 20
    ) -> List[User]:
        """
        Get users who have been active within the specified days.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of users to return
            
        Returns:
            List of recently active users
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = (
            select(User)
            .where(and_(
                User.is_deleted == False,
                User.last_login >= cutoff_date
            ))
            .order_by(desc(User.last_login))
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get user statistics for dashboard.
        
        Returns:
            Dictionary with user statistics
        """
        # Total users
        total_query = select(func.count(User.id)).where(User.is_deleted == False)
        total_users = await self.db.scalar(total_query) or 0
        
        # Active users
        active_query = select(func.count(User.id)).where(and_(
            User.is_active == True,
            User.is_deleted == False
        ))
        active_users = await self.db.scalar(active_query) or 0
        
        # Users by role
        role_query = (
            select(User.role, func.count(User.id))
            .where(User.is_deleted == False)
            .group_by(User.role)
        )
        role_result = await self.db.execute(role_query)
        users_by_role = dict(role_result.fetchall())
        
        # Recent registrations (last 30 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_query = select(func.count(User.id)).where(and_(
            User.created_at >= recent_date,
            User.is_deleted == False
        ))
        recent_registrations = await self.db.scalar(recent_query) or 0
        
        # Recent logins (last 30 days)
        recent_login_query = select(func.count(User.id)).where(and_(
            User.last_login >= recent_date,
            User.is_deleted == False
        ))
        recent_logins = await self.db.scalar(recent_login_query) or 0
        
        return {
            'total': total_users,
            'active': active_users,
            'inactive': total_users - active_users,
            'by_role': users_by_role,
            'recent_registrations': recent_registrations,
            'recent_logins': recent_logins
        }

    async def update_last_login(self, user_id: UUID) -> bool:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User UUID
            
        Returns:
            True if updated successfully
        """
        from sqlalchemy import update
        
        query = (
            update(User)
            .where(and_(User.id == user_id, User.is_deleted == False))
            .values(
                last_login=datetime.utcnow(),
                login_count=User.login_count + 1
            )
        )
        
        result = await self.db.execute(query)
        return result.rowcount > 0

    async def get_users_with_filters(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 50
    ) -> List[User]:
        """
        Get users with advanced filtering.
        
        Args:
            filters: Dictionary of filters to apply
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of filtered users
        """
        query = select(User).where(User.is_deleted == False)
        
        # Apply filters
        if filters.get('role'):
            query = query.where(User.role == filters['role'])
        
        if filters.get('is_active') is not None:
            query = query.where(User.is_active == filters['is_active'])
        
        if filters.get('query'):
            search_pattern = f"%{filters['query']}%"
            query = query.where(or_(
                User.email.ilike(search_pattern),
                User.display_name.ilike(search_pattern)
            ))
        
        if filters.get('created_after'):
            query = query.where(User.created_at >= filters['created_after'])
        
        if filters.get('created_before'):
            query = query.where(User.created_at <= filters['created_before'])
        
        if filters.get('last_login_after'):
            query = query.where(User.last_login >= filters['last_login_after'])
        
        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def bulk_update_role(
        self,
        user_ids: List[UUID],
        new_role: str,
        updated_by: Optional[UUID] = None
    ) -> int:
        """
        Update role for multiple users.
        
        Args:
            user_ids: List of user IDs
            new_role: New role to assign
            updated_by: User performing the update
            
        Returns:
            Number of users updated
        """
        from sqlalchemy import update
        
        update_data = {"role": new_role}
        if updated_by:
            update_data["updated_by"] = updated_by
        
        query = (
            update(User)
            .where(and_(
                User.id.in_(user_ids),
                User.is_deleted == False
            ))
            .values(**update_data)
        )
        
        result = await self.db.execute(query)
        return result.rowcount

    async def deactivate_inactive_users(self, days_inactive: int = 365) -> int:
        """
        Deactivate users who haven't logged in for specified days.
        
        Args:
            days_inactive: Number of days of inactivity
            
        Returns:
            Number of users deactivated
        """
        from sqlalchemy import update
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
        
        query = (
            update(User)
            .where(and_(
                User.last_login < cutoff_date,
                User.is_active == True,
                User.is_deleted == False
            ))
            .values(is_active=False)
        )
        
        result = await self.db.execute(query)
        return result.rowcount

    async def get_admin_users(self) -> List[User]:
        """
        Get all admin users.
        
        Returns:
            List of admin users
        """
        query = (
            select(User)
            .where(and_(
                User.role == "admin",
                User.is_active == True,
                User.is_deleted == False
            ))
            .order_by(User.created_at)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_user_activity_summary(
        self,
        user_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get activity summary for a user.
        
        Args:
            user_id: User UUID
            days: Number of days to analyze
            
        Returns:
            Dictionary with activity summary
        """
        user = await self.get_by_id(user_id)
        if not user:
            return {}
        
        # This would typically involve querying audit logs or activity tables
        # For now, return basic user information
        return {
            'user_id': user_id,
            'total_logins': user.login_count,
            'last_login': user.last_login,
            'account_age_days': (datetime.utcnow() - user.created_at).days,
            'is_active': user.is_active,
            'role': user.role
        }
