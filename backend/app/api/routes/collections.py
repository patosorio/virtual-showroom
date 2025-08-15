"""
Collection API Routes

REST API endpoints for collection management.
Handles CRUD operations, filtering, and collection-specific features.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.collection import CollectionService
from app.schemas.collection import (
    CollectionCreate, CollectionUpdate, CollectionResponse,
    CollectionSummary, CollectionListFilters, CollectionPublishRequest,
    CollectionAnalytics
)
from app.schemas.base import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse[CollectionResponse],
    summary="List collections",
    description="Get a paginated list of collections with optional filtering"
)
async def list_collections(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    season: Optional[str] = Query(None, description="Filter by season"),
    year: Optional[int] = Query(None, description="Filter by year"),
    collection_status: Optional[str] = Query(None, description="Filter by status"),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    query: Optional[str] = Query(None, description="Search query"),
    has_products: Optional[bool] = Query(None, description="Filter collections with/without products"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """List collections with pagination and filtering."""
    try:
        service = CollectionService(db)
        
        # Build filters
        filters = CollectionListFilters(
            season=season,
            year=year,
            status=collection_status,
            is_published=is_published,
            query=query,
            has_products=has_products
        )
        
        # Get collections
        collections, total = await service.list_collections(
            filters=filters,
            skip=skip,
            limit=limit,
            user_id=current_user["uid"] if current_user else None
        )
        
        # Convert to response models manually to avoid relationship access issues
        collection_responses = []
        for collection in collections:
            response_data = {
                "id": collection.id,
                "name": collection.name,
                "slug": collection.slug,
                "season": collection.season,
                "year": collection.year,
                "description": collection.description,
                "short_description": collection.short_description,
                "order_start_date": collection.order_start_date,
                "order_end_date": collection.order_end_date,
                "seo_title": collection.seo_title,
                "seo_description": collection.seo_description,
                "metadata": collection.extra_data if isinstance(collection.extra_data, dict) else {},  # Map extra_data to metadata
                "status": collection.status,
                "is_published": collection.is_published,
                "product_count": collection.product_count,
                "is_order_period_active": collection.is_order_period_active,
                "full_name": collection.full_name,
                "created_at": collection.created_at,
                "updated_at": collection.updated_at,
                "created_by": collection.created_by,
                "updated_by": collection.updated_by,
                "is_deleted": collection.is_deleted,
                "deleted_at": collection.deleted_at,
                "notes": collection.notes,
                "products": None,  # Don't include relationships for list
                "files": None     # Don't include relationships for list
            }
            collection_responses.append(CollectionResponse.model_validate(response_data))
        
        return PaginatedResponse.create(
            items=collection_responses,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        import traceback
        print("Error in list_collections:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while listing collections: {str(e)}"
        )


@router.post(
    "/",
    response_model=CollectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create collection",
    description="Create a new collection (admin only)"
)
async def create_collection(
    collection_data: CollectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new collection."""
    try:
        service = CollectionService(db)
        
        collection = await service.create_collection(
            data=collection_data,
            user_id=current_user["uid"]
        )
        
        # Convert to response dict manually to avoid relationship access issues
        response_data = {
            "id": collection.id,
            "name": collection.name,
            "slug": collection.slug,
            "season": collection.season,
            "year": collection.year,
            "description": collection.description,
            "short_description": collection.short_description,
            "order_start_date": collection.order_start_date,
            "order_end_date": collection.order_end_date,
            "seo_title": collection.seo_title,
            "seo_description": collection.seo_description,
            "metadata": collection.extra_data if isinstance(collection.extra_data, dict) else {},
            "status": collection.status,
            "is_published": collection.is_published,
            "product_count": collection.product_count,
            "is_order_period_active": collection.is_order_period_active,
            "full_name": collection.full_name,
            "created_at": collection.created_at,
            "updated_at": collection.updated_at,
            "created_by": collection.created_by,
            "updated_by": collection.updated_by,
            "is_deleted": collection.is_deleted,
            "deleted_at": collection.deleted_at,
            "notes": collection.notes,
            "products": None,  # Don't include relationships for create
            "files": None     # Don't include relationships for create
        }
        
        return CollectionResponse.model_validate(response_data)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        import traceback
        print("Error in create_collection:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the collection: {str(e)}"
        )


@router.get(
    "/{collection_id}",
    response_model=CollectionResponse,
    summary="Get collection by ID",
    description="Get a specific collection by its UUID"
)
async def get_collection(
    collection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get a collection by ID."""
    try:
        service = CollectionService(db)
        
        collection = await service.get_by_id(
            id=collection_id,
            user_id=UUID(current_user["uid"]) if current_user else None
        )
        
        return CollectionResponse.model_validate(collection)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the collection"
        )


@router.get(
    "/slug/{slug}",
    response_model=CollectionResponse,
    summary="Get collection by slug",
    description="Get a specific collection by its URL slug"
)
async def get_collection_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get a collection by slug."""
    try:
        service = CollectionService(db)
        
        collection = await service.get_collection_by_slug(slug)
        
        return CollectionResponse.model_validate(collection)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the collection"
        )


@router.put(
    "/{collection_id}",
    response_model=CollectionResponse,
    summary="Update collection",
    description="Update an existing collection (admin only)"
)
async def update_collection(
    collection_id: UUID,
    collection_data: CollectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a collection."""
    try:
        service = CollectionService(db)
        
        collection = await service.update_collection(
            collection_id=collection_id,
            data=collection_data,
            user_id=UUID(current_user["uid"])
        )
        
        return CollectionResponse.model_validate(collection)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the collection"
        )


@router.delete(
    "/{collection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete collection",
    description="Soft delete a collection (admin only)"
)
async def delete_collection(
    collection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a collection."""
    try:
        service = CollectionService(db)
        
        await service.delete(
            id=collection_id,
            user_id=UUID(current_user["uid"])
        )
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the collection"
        )


@router.post(
    "/{collection_id}/publish",
    response_model=CollectionResponse,
    summary="Publish/unpublish collection",
    description="Change collection publication status (admin only)"
)
async def publish_collection(
    collection_id: UUID,
    publish_data: CollectionPublishRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Publish or unpublish a collection."""
    try:
        service = CollectionService(db)
        
        collection = await service.publish_collection(
            collection_id=collection_id,
            publish=publish_data.publish,
            user_id=UUID(current_user["uid"])
        )
        
        return CollectionResponse.model_validate(collection)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating publication status"
        )


@router.get(
    "/{collection_id}/analytics",
    response_model=CollectionAnalytics,
    summary="Get collection analytics",
    description="Get detailed analytics for a collection (admin only)"
)
async def get_collection_analytics(
    collection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get analytics for a collection."""
    try:
        service = CollectionService(db)
        
        analytics = await service.get_collection_analytics(collection_id)
        
        return analytics
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving analytics"
        )


@router.get(
    "/featured/",
    response_model=List[CollectionResponse],
    summary="Get featured collections",
    description="Get collections that contain featured products"
)
async def get_featured_collections(
    limit: int = Query(6, ge=1, le=20, description="Number of collections to return"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get featured collections."""
    try:
        service = CollectionService(db)
        
        collections = await service.get_featured_collections(limit=limit)
        
        return [
            CollectionResponse.model_validate(collection)
            for collection in collections
        ]
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving featured collections"
        )


@router.get(
    "/search/",
    response_model=List[CollectionResponse],
    summary="Search collections",
    description="Search collections by name or description"
)
async def search_collections(
    q: str = Query(..., min_length=2, description="Search query"),
    published_only: bool = Query(True, description="Only search published collections"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Search collections."""
    try:
        service = CollectionService(db)
        
        collections = await service.search_collections(
            query=q,
            published_only=published_only,
            skip=skip,
            limit=limit
        )
        
        return [
            CollectionResponse.model_validate(collection)
            for collection in collections
        ]
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while searching collections"
        )