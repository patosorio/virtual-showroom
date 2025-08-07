"""
Authentication Pydantic Schemas

Schemas for authentication, user management, and authorization.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import Field, EmailStr, field_validator

from .base import BaseSchema, BaseResponseSchema


# Authentication Schemas

class LoginRequest(BaseSchema):
    """Login request schema."""
    
    id_token: str = Field(..., description="Firebase ID token")


class LoginResponse(BaseSchema):
    """Login response schema."""
    
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")
    user: "UserResponse" = Field(description="User information")


class RefreshTokenRequest(BaseSchema):
    """Refresh token request schema."""
    
    refresh_token: str = Field(..., description="Firebase refresh token")


class RefreshTokenResponse(BaseSchema):
    """Refresh token response schema."""
    
    access_token: str = Field(description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")


class LogoutRequest(BaseSchema):
    """Logout request schema."""
    
    everywhere: bool = Field(default=False, description="Logout from all devices")


# User Management Schemas

class UserBase(BaseSchema):
    """Base user schema."""
    
    email: EmailStr = Field(..., description="User email address")
    display_name: Optional[str] = Field(None, max_length=100, description="Display name")
    photo_url: Optional[str] = Field(None, description="Profile photo URL")
    phone_number: Optional[str] = Field(None, description="Phone number")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if not v:
            return v
        
        import re
        # Basic phone number validation (international format)
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError("Phone number must be in international format (e.g., +1234567890)")
        
        return v


class UserCreate(UserBase):
    """Schema for creating a user."""
    
    firebase_uid: str = Field(..., description="Firebase UID")
    role: str = Field(default="user", description="User role")
    is_active: bool = Field(default=True, description="Whether user is active")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate user role."""
        valid_roles = ["admin", "user", "viewer"]
        if v not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return v


class UserUpdate(BaseSchema):
    """Schema for updating a user."""
    
    display_name: Optional[str] = Field(None, max_length=100, description="Display name")
    photo_url: Optional[str] = Field(None, description="Profile photo URL")
    phone_number: Optional[str] = Field(None, description="Phone number")
    role: Optional[str] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="Whether user is active")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        """Validate user role."""
        if v:
            valid_roles = ["admin", "user", "viewer"]
            if v not in valid_roles:
                raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return v
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if not v:
            return v
        
        import re
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError("Phone number must be in international format")
        
        return v


class UserResponse(UserBase, BaseResponseSchema):
    """Schema for user response."""
    
    firebase_uid: str
    role: str
    is_active: bool
    last_login: Optional[str] = Field(None, description="Last login timestamp")
    login_count: int = Field(default=0, description="Total login count")


class UserProfile(BaseSchema):
    """User profile schema for current user."""
    
    id: UUID
    email: EmailStr
    display_name: Optional[str]
    photo_url: Optional[str]
    phone_number: Optional[str]
    role: str
    is_active: bool
    last_login: Optional[str]
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User preferences")


class UserProfileUpdate(BaseSchema):
    """Schema for updating user profile."""
    
    display_name: Optional[str] = Field(None, max_length=100, description="Display name")
    photo_url: Optional[str] = Field(None, description="Profile photo URL")
    phone_number: Optional[str] = Field(None, description="Phone number")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if not v:
            return v
        
        import re
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError("Phone number must be in international format")
        
        return v


# Permission and Role Schemas

class PermissionSchema(BaseSchema):
    """Permission schema."""
    
    resource: str = Field(..., description="Resource name (e.g., 'products', 'collections')")
    action: str = Field(..., description="Action name (e.g., 'create', 'read', 'update', 'delete')")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Additional permission conditions")


class RoleSchema(BaseSchema):
    """Role schema."""
    
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    permissions: List[PermissionSchema] = Field(description="List of permissions")


class UserRoleUpdate(BaseSchema):
    """Schema for updating user role."""
    
    role: str = Field(..., description="New role")
    reason: Optional[str] = Field(None, description="Reason for role change")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate user role."""
        valid_roles = ["admin", "user", "viewer"]
        if v not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return v


# Session and Token Schemas

class ActiveSession(BaseSchema):
    """Active session schema."""
    
    session_id: str = Field(description="Session identifier")
    device_info: Optional[str] = Field(None, description="Device information")
    ip_address: Optional[str] = Field(None, description="IP address")
    location: Optional[str] = Field(None, description="Geographic location")
    created_at: str = Field(description="Session creation time")
    last_activity: str = Field(description="Last activity time")
    is_current: bool = Field(description="Whether this is the current session")


class TokenValidationResponse(BaseSchema):
    """Token validation response."""
    
    is_valid: bool = Field(description="Whether token is valid")
    user_id: Optional[UUID] = Field(None, description="User ID if token is valid")
    expires_at: Optional[str] = Field(None, description="Token expiration time")
    permissions: Optional[List[str]] = Field(None, description="User permissions")


# Password and Security Schemas

class PasswordResetRequest(BaseSchema):
    """Password reset request schema."""
    
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation schema."""
    
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        import re
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one number")
        
        return v


class PasswordChangeRequest(BaseSchema):
    """Password change request schema."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        import re
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one number")
        
        return v


# Two-Factor Authentication Schemas

class TwoFactorSetupRequest(BaseSchema):
    """2FA setup request schema."""
    
    phone_number: Optional[str] = Field(None, description="Phone number for SMS 2FA")
    method: str = Field(default="sms", description="2FA method")
    
    @field_validator('method')
    @classmethod
    def validate_2fa_method(cls, v: str) -> str:
        """Validate 2FA method."""
        valid_methods = ["sms", "email", "app"]
        if v not in valid_methods:
            raise ValueError(f"2FA method must be one of: {', '.join(valid_methods)}")
        return v


class TwoFactorVerifyRequest(BaseSchema):
    """2FA verification request schema."""
    
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    
    @field_validator('code')
    @classmethod
    def validate_code_format(cls, v: str) -> str:
        """Validate verification code format."""
        if not v.isdigit():
            raise ValueError("Verification code must be 6 digits")
        return v


class TwoFactorBackupCodes(BaseSchema):
    """2FA backup codes schema."""
    
    codes: List[str] = Field(description="List of backup codes")
    generated_at: str = Field(description="Generation timestamp")


# API Key Management Schemas

class APIKeyCreate(BaseSchema):
    """API key creation schema."""
    
    name: str = Field(..., max_length=100, description="API key name")
    description: Optional[str] = Field(None, max_length=500, description="API key description")
    expires_at: Optional[str] = Field(None, description="Expiration date")
    permissions: List[str] = Field(default_factory=list, description="API key permissions")


class APIKeyResponse(BaseSchema):
    """API key response schema."""
    
    id: UUID
    name: str
    description: Optional[str]
    key_preview: str = Field(description="First few characters of the key")
    created_at: str
    expires_at: Optional[str]
    last_used: Optional[str]
    is_active: bool
    permissions: List[str]


class APIKeyUpdate(BaseSchema):
    """API key update schema."""
    
    name: Optional[str] = Field(None, max_length=100, description="API key name")
    description: Optional[str] = Field(None, max_length=500, description="API key description")
    expires_at: Optional[str] = Field(None, description="Expiration date")
    is_active: Optional[bool] = Field(None, description="Whether key is active")
    permissions: Optional[List[str]] = Field(None, description="API key permissions")


# Forward reference
UserResponse.model_rebuild()
