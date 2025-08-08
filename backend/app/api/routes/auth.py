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
    description="Authenticate user with Firebase token and create/get user"
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """User login with Firebase token."""
    try:
        from app.core.firebase.auth import verify_firebase_token
        from app.schemas.auth import UserCreate
        
        # Verify Firebase token
        firebase_user = await verify_firebase_token(login_data.id_token)
        
        # Get or create user in our database
        service = AuthService(db)
        
        try:
            # Try to get existing user
            user = await service.get_user_by_firebase_uid(firebase_user["uid"])
        except Exception:
            # User doesn't exist, create new one
            user_data = UserCreate(
                email=firebase_user.get("email"),
                firebase_uid=firebase_user["uid"],
                display_name=firebase_user.get("name") or firebase_user.get("email", "").split("@")[0],
                photo_url=firebase_user.get("picture"),
                role="user",
                is_active=True
            )
            user = await service.create_user(user_data)
            await db.commit()  # Commit the user creation
        
        # Record login activity
        await service.record_login(user.id)
        await db.commit()  # Commit the login activity
        
        return LoginResponse(
            access_token=login_data.id_token,  # We'll use the Firebase token
            token_type="bearer",
            expires_in=3600,
            user=UserResponse(
                id=user.id,
                email=user.email,
                firebase_uid=user.firebase_uid,
                role=user.role,
                is_active=user.is_active,
                display_name=user.display_name,
                created_at=user.created_at.isoformat(),
                updated_at=user.updated_at.isoformat()
            )
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during authentication: {str(e)}"
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
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Getting profile for user: {current_user}")
        
        from app.schemas.auth import UserCreate
        
        service = AuthService(db)
        
        try:
            # Try to get existing user
            logger.info(f"Looking for user with Firebase UID: {current_user['uid']}")
            user = await service.get_user_by_firebase_uid(current_user["uid"])
            logger.info(f"Found existing user: {user.email}")
        except Exception as e:
            logger.info(f"User not found, creating new user. Error: {str(e)}")
            # User doesn't exist in our database, create them
            user_data = UserCreate(
                email=current_user.get("email"),
                firebase_uid=current_user["uid"],
                display_name=current_user.get("name") or current_user.get("email", "").split("@")[0],
                photo_url=current_user.get("picture"),
                role="user",
                is_active=True
            )
            logger.info(f"Creating user with data: {user_data.model_dump()}")
            user = await service.create_user(user_data)
            await db.commit()  # Commit the user creation
            logger.info(f"Created new user: {user.email}")
            
        # Record login activity
        await service.record_login(user.id)
        await db.commit()  # Commit the login activity
        
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
        raise e
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in get_current_user_profile: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving user profile: {str(e)}"
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