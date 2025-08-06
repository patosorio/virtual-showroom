"""
Collections API Routes

RESTful endpoints for managing fashion collections in the Virtual Showroom.
Follows clean architecture with proper separation of concerns.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.core.config import get_settings
from app.models.user import User
from app.schemas.collection import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionListResponse,
)
from app.services.collection import CollectionService

router = APIRouter()
settings = get_settings()


@router.get(
    "/",
    response_model=CollectionListResponse,
    summary="List Collections",
    description="Retrieve a paginated list of collections with optional filtering.",
)
async def list_collections(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        default=settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Number of records to return",
    ),
    season: Optional[str] = Query(default=None, description="Filter by season"),
    year: Optional[int] = Query(default=None, description="Filter by year"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    search: Optional[str] = Query(default=None, description="Search in name and description"),
) -> CollectionListResponse:
    """
    Retrieve collections with pagination and filtering.
    
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    - **season**: Filter by collection season
    - **year**: Filter by collection year
    - **status**: Filter by collection status
    - **search**: Search term for name and description
    """
    service = CollectionService(db)
    
    collections, total = await service.get_collections(
        skip=skip,
        limit=limit,
        season=season,
        year=year,
        status=status,
        search=search,
    )
    
    return CollectionListResponse(
        items=collections,
        total=total,
        page=skip // limit + 1,
        pages=(total + limit - 1) // limit,
        size=len(collections),
    )


@router.get(
    "/{collection_id}",
    response_model=CollectionResponse,
    summary="Get Collection",
    description="Retrieve a specific collection by ID with all related data.",
)
async def get_collection(
    collection_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CollectionResponse:
    """
    Retrieve a specific collection by ID.
    
    - **collection_id**: UUID of the collection to retrieve
    """
    service = CollectionService(db)
    
    collection = await service.get_collection(collection_id)
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    return collection


@router.get(
    "/slug/{slug}",
    response_model=CollectionResponse,
    summary="Get Collection by Slug",
    description="Retrieve a specific collection by its URL slug.",
)
async def get_collection_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> CollectionResponse:
    """
    Retrieve a collection by its URL slug.
    
    - **slug**: URL-friendly slug of the collection
    """
    service = CollectionService(db)
    
    collection = await service.get_collection_by_slug(slug)
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    return collection


@router.post(
    "/",
    response_model=CollectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Collection",
    description="Create a new fashion collection.",
)
async def create_collection(
    collection_data: CollectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CollectionResponse:
    """
    Create a new collection.
    
    - **collection_data**: Collection data to create
    """
    service = CollectionService(db)
    
    # Check if slug already exists
    existing = await service.get_collection_by_slug(collection_data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Collection with this slug already exists"
        )
    
    collection = await service.create_collection(collection_data, current_user.id)
    return collection


@router.put(
    "/{collection_id}",
    response_model=CollectionResponse,
    summary="Update Collection",
    description="Update an existing collection.",
)
async def update_collection(
    collection_id: UUID,
    collection_data: CollectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CollectionResponse:
    """
    Update an existing collection.
    
    - **collection_id**: UUID of the collection to update
    - **collection_data**: Updated collection data
    """
    service = CollectionService(db)
    
    # Check if collection exists
    existing = await service.get_collection(collection_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Check slug uniqueness if changed
    if collection_data.slug and collection_data.slug != existing.slug:
        slug_exists = await service.get_collection_by_slug(collection_data.slug)
        if slug_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Collection with this slug already exists"
            )
    
    collection = await service.update_collection(
        collection_id, collection_data, current_user.id
    )
    return collection


@router.delete(
    "/{collection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Collection",
    description="Soft delete a collection and all related data.",
)
async def delete_collection(
    collection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a collection (soft delete).
    
    - **collection_id**: UUID of the collection to delete
    """
    service = CollectionService(db)
    
    success = await service.delete_collection(collection_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )


@router.get(
    "/{collection_id}/products",
    response_model=List[dict],  # Will be properly typed when ProductResponse is created
    summary="Get Collection Products",
    description="Retrieve all products in a specific collection.",
)
async def get_collection_products(
    collection_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    Get all products in a collection.
    
    - **collection_id**: UUID of the collection
    """
    service = CollectionService(db)
    
    collection = await service.get_collection(collection_id)
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    products = await service.get_collection_products(collection_id)
    return products


@router.post(
    "/{collection_id}/publish",
    response_model=CollectionResponse,
    summary="Publish Collection",
    description="Publish a collection to make it publicly visible.",
)
async def publish_collection(
    collection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CollectionResponse:
    """
    Publish a collection.
    
    - **collection_id**: UUID of the collection to publish
    """
    service = CollectionService(db)
    
    collection = await service.publish_collection(collection_id, current_user.id)
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    return collection


@router.post(
    "/{collection_id}/unpublish",
    response_model=CollectionResponse,
    summary="Unpublish Collection",
    description="Unpublish a collection to make it private.",
)
async def unpublish_collection(
    collection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CollectionResponse:
    """
    Unpublish a collection.
    
    - **collection_id**: UUID of the collection to unpublish
    """
    service = CollectionService(db)
    
    collection = await service.unpublish_collection(collection_id, current_user.id)
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    return collection