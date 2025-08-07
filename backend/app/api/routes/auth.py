"""
Authentication API Routes

REST API endpoints for user authentication and management.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.auth import AuthService
from app.schemas.auth import (
    LoginRequest, LoginResponse, UserCreate, UserUpdate, UserResponse,
    UserProfile, UserProfileUpdate, UserRoleUpdate
)
from fastapi import HTTPException

router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    description="Authenticate user with Firebase token"
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """User login with Firebase token."""
    try:
        # This would validate Firebase token and create/get user
        # For now, return placeholder response
        return LoginResponse(
            access_token="placeholder_token",
            token_type="bearer",
            expires_in=3600,
            user=UserResponse(
                id=UUID(),
                email="user@example.com",
                firebase_uid="firebase_uid",
                role="user",
                is_active=True,
                display_name="User Name",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z"
            )
        )
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during authentication"
        )


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current user profile",
    description="Get the current user's profile information"
)
async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current user profile."""
    try:
        service = AuthService(db)
        
        user = await service.get_user_by_firebase_uid(current_user["uid"])
        
        return UserProfile(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            photo_url=user.photo_url,
            phone_number=user.phone_number,
            role=user.role,
            is_active=user.is_active,
            last_login=user.last_login.isoformat() if user.last_login else None,
            preferences={}
        )
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving user profile"
        )


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    description="Update the current user's profile information"
)
async def update_current_user_profile(
    profile_data: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile."""
    try:
        service = AuthService(db)
        
        user = await service.update_user_profile(
            user_id=UUID(current_user["uid"]),
            data=profile_data,
            current_user_id=UUID(current_user["uid"])
        )
        
        return UserResponse.model_validate(user)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user profile"
        )


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create a new user account (admin only)"
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new user."""
    try:
        service = AuthService(db)
        
        user = await service.create_user(
            data=user_data,
            user_id=UUID(current_user["uid"])
        )
        
        return UserResponse.model_validate(user)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user"
        )


@router.patch(
    "/users/{user_id}/role",
    response_model=UserResponse,
    summary="Update user role",
    description="Update a user's role (admin only)"
)
async def update_user_role(
    user_id: UUID,
    role_data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update user role."""
    try:
        service = AuthService(db)
        
        user = await service.update_user_role(
            user_id=user_id,
            role_data=role_data,
            admin_user_id=UUID(current_user["uid"])
        )
        
        return UserResponse.model_validate(user)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user role"
        )
