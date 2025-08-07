"""
FastAPI Dependencies

Dependency injection for services, authentication, and common utilities.
"""

from typing import Optional, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.firebase.auth import verify_firebase_token
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.services.product import ProductService
from app.services.collection import CollectionService

# Security scheme for JWT tokens
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get current authenticated user from Firebase token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        User data from Firebase token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        token = credentials.credentials
        user_data = await verify_firebase_token(token)
        return user_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[dict]:
    """
    Get current user if authenticated, otherwise return None.
    
    Args:
        credentials: Optional HTTP authorization credentials
        
    Returns:
        User data if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_data = await verify_firebase_token(token)
        return user_data
    except Exception:
        return None


async def get_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get current user and verify admin permissions.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Admin user data
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.get("admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required"
        )
    
    return current_user


# Service Dependencies

async def get_product_service(
    db: AsyncSession = Depends(get_db)
) -> ProductService:
    """
    Get Product service instance.
    
    Args:
        db: Database session
        
    Returns:
        ProductService instance
    """
    return ProductService(db)


async def get_collection_service(
    db: AsyncSession = Depends(get_db)
) -> CollectionService:
    """
    Get Collection service instance.
    
    Args:
        db: Database session
        
    Returns:
        CollectionService instance
    """
    return CollectionService(db)


# Utility Dependencies

async def get_pagination_params(
    skip: int = 0,
    limit: int = 20
) -> dict:
    """
    Get validated pagination parameters.
    
    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        
    Returns:
        Dictionary with pagination parameters
        
    Raises:
        HTTPException: If parameters are invalid
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip parameter cannot be negative"
        )
    
    if limit <= 0 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit parameter must be between 1 and 100"
        )
    
    return {"skip": skip, "limit": limit}


def get_user_id(current_user: dict = Depends(get_current_user)) -> str:
    """
    Extract user ID from current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User ID string
    """
    return current_user.get("uid") or current_user.get("user_id")


def get_user_id_optional(
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> Optional[str]:
    """
    Extract user ID from current user if authenticated.
    
    Args:
        current_user: Current authenticated user or None
        
    Returns:
        User ID string or None
    """
    if not current_user:
        return None
    
    return current_user.get("uid") or current_user.get("user_id")