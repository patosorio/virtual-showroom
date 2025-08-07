"""
User Database Model

Represents user accounts and authentication information.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Index
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


class User(BaseModel):
    """
    User Model
    
    Represents user accounts for authentication and authorization.
    Integrates with Firebase Authentication.
    """
    __tablename__ = "users"
    
    # Authentication Information
    firebase_uid = Column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        doc="Firebase UID for authentication"
    )
    
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="User email address"
    )
    
    # Profile Information
    display_name = Column(
        String(100),
        nullable=True,
        doc="User display name"
    )
    
    photo_url = Column(
        String(500),
        nullable=True,
        doc="Profile photo URL"
    )
    
    phone_number = Column(
        String(20),
        nullable=True,
        doc="User phone number"
    )
    
    # Authorization and Status
    role = Column(
        String(20),
        default="user",
        nullable=False,
        index=True,
        doc="User role (admin, user, viewer)"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="Whether user account is active"
    )
    
    # Activity Tracking
    last_login = Column(
        DateTime,
        nullable=True,
        doc="Last login timestamp"
    )
    
    login_count = Column(
        Integer,
        default=0,
        nullable=False,
        doc="Total number of logins"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_user_email_active", "email", "is_active"),
        Index("idx_user_role_active", "role", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<User(email='{self.email}', role='{self.role}')>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == "admin"
    
    @property
    def full_profile(self) -> dict:
        """Get full user profile information."""
        return {
            "id": str(self.id),
            "email": self.email,
            "display_name": self.display_name,
            "photo_url": self.photo_url,
            "phone_number": self.phone_number,
            "role": self.role,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "login_count": self.login_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
