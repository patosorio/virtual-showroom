"""
Collection Service

Business logic layer for Collection entity.
Handles collection business rules, validation, and complex operations.
"""

import re
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection
from app.repositories.collection import CollectionRepository
from app.services.base import BaseService
from app.core.exceptions import (
    ValidationError, ConflictError, NotFoundError, 
    BadRequestError, ForbiddenError
)


class CollectionService(BaseService[Collection, CollectionRepository]):
    """
    Collection service with business logic.
    
    Manages collection lifecycle, validation, and business operations.
    """

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        super().__init__(db, CollectionRepository, Collection)

    async def get_for_display(self, collection_id: UUID) -> Collection:
        """
        Get collection for frontend display with business rules.
        
        Business rule: Only return published collections with products.
        
        Args:
            collection_id: Collection UUID
            
        Returns:
            Collection with products loaded
            
        Raises:
            NotFoundError: If collection doesn't exist or isn't published
        """
        collection = await self.repository.get_with_products(collection_id)
        
        if not collection:
            raise NotFoundError(
                detail=f"Collection with ID {collection_id} not found",
                error_code="COLLECTION_NOT_FOUND",
                context={"collection_id": str(collection_id)}
            )
        
        # Business rule: Collection must be published
        if not collection.is_published:
            raise NotFoundError(
                detail="Collection is not available for viewing",
                error_code="COLLECTION_NOT_PUBLISHED",
                context={"collection_id": str(collection_id)}
            )
        
        return collection

    async def get_by_slug(self, slug: str) -> Collection:
        """
        Get collection by slug for frontend routing.
        
        Args:
            slug: Collection URL slug
            
        Returns:
            Collection
            
        Raises:
            NotFoundError: If collection doesn't exist or isn't published
        """
        collection = await self.repository.get_by_slug(slug)
        
        if not collection:
            raise NotFoundError(
                detail=f"Collection with slug '{slug}' not found",
                error_code="COLLECTION_NOT_FOUND",
                context={"slug": slug}
            )
        
        if not collection.is_published:
            raise NotFoundError(
                detail="Collection is not available for viewing",
                error_code="COLLECTION_NOT_PUBLISHED",
                context={"slug": slug}
            )
        
        return collection

    async def get_published_collections(
        self,
        skip: int = 0,
        limit: int = 20,
        season: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[Collection]:
        """
        Get published collections with business validation.
        
        Args:
            skip: Pagination offset
            limit: Pagination limit
            season: Optional season filter
            year: Optional year filter
            
        Returns:
            List of published collections
        """
        # Validate pagination
        await self._validate_pagination(skip, limit)
        
        # Validate filters
        if season and not await self._is_valid_season(season):
            raise ValidationError(
                detail=f"Invalid season: {season}",
                error_code="INVALID_SEASON",
                context={"season": season}
            )
        
        if year and not await self._is_valid_year(year):
            raise ValidationError(
                detail=f"Invalid year: {year}",
                error_code="INVALID_YEAR",
                context={"year": year}
            )
        
        return await self.repository.get_published_collections(skip, limit, season, year)

    async def create_collection(
        self,
        data: Dict[str, Any],
        user_id: Optional[UUID] = None
    ) -> Collection:
        """
        Create new collection with business validation.
        
        Args:
            data: Collection data
            user_id: ID of creating user
            
        Returns:
            Created collection
        """
        return await self.create(data, user_id)

    async def update_collection(
        self,
        collection_id: UUID,
        data: Dict[str, Any],
        user_id: Optional[UUID] = None
    ) -> Collection:
        """
        Update collection with business validation.
        
        Args:
            collection_id: Collection UUID
            data: Updated data
            user_id: ID of updating user
            
        Returns:
            Updated collection
        """
        return await self.update(collection_id, data, user_id)

    async def publish_collection(
        self,
        collection_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Collection:
        """
        Publish a collection.
        
        Business rule: Collection must have at least one active product to be published.
        
        Args:
            collection_id: Collection UUID
            user_id: ID of user publishing
            
        Returns:
            Published collection
            
        Raises:
            ValidationError: If collection cannot be published
        """
        collection = await self.get_by_id(collection_id, user_id)
        
        # Business rule: Must have active products
        active_products = [p for p in collection.products if p.status == "active" and not p.is_deleted]
        if not active_products:
            raise ValidationError(
                detail="Cannot publish collection without active products",
                error_code="COLLECTION_NO_ACTIVE_PRODUCTS",
                context={"collection_id": str(collection_id)}
            )
        
        return await self.update_collection(
            collection_id,
            {"is_published": True},
            user_id
        )

    async def unpublish_collection(
        self,
        collection_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Collection:
        """
        Unpublish a collection.
        
        Args:
            collection_id: Collection UUID
            user_id: ID of user unpublishing
            
        Returns:
            Unpublished collection
        """
        return await self.update_collection(
            collection_id,
            {"is_published": False},
            user_id
        )

    async def search_collections(
        self,
        search_term: str,
        published_only: bool = True,
        skip: int = 0,
        limit: int = 20
    ) -> List[Collection]:
        """
        Search collections with business validation.
        
        Args:
            search_term: Search text
            published_only: Whether to only search published collections
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of matching collections
        """
        # Business rule: Search term must be meaningful
        if len(search_term.strip()) < 2:
            raise ValidationError(
                detail="Search term must be at least 2 characters",
                error_code="INVALID_SEARCH_TERM",
                context={"search_term": search_term}
            )
        
        return await self.repository.search_collections(
            search_term, published_only, skip, limit
        )

    # Business Logic Validation Methods

    async def _validate_create_data(
        self,
        data: Dict[str, Any],
        user_id: Optional[UUID]
    ) -> None:
        """Validate collection creation data."""
        
        # Required fields
        required_fields = ["name", "season", "year"]
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(
                    detail=f"Field '{field}' is required",
                    error_code="MISSING_REQUIRED_FIELD",
                    context={"field": field}
                )
        
        # Season validation
        if not await self._is_valid_season(data["season"]):
            raise ValidationError(
                detail=f"Invalid season: {data['season']}",
                error_code="INVALID_SEASON",
                context={"season": data["season"]}
            )
        
        # Year validation
        if not await self._is_valid_year(data["year"]):
            raise ValidationError(
                detail=f"Invalid year: {data['year']}",
                error_code="INVALID_YEAR",
                context={"year": data["year"]}
            )
        
        # Name length validation
        if len(data["name"]) > 100:
            raise ValidationError(
                detail="Collection name cannot exceed 100 characters",
                error_code="NAME_TOO_LONG",
                context={"name": data["name"], "length": len(data["name"])}
            )
        
        # Order dates validation
        if data.get("order_start_date") and data.get("order_end_date"):
            start_date = data["order_start_date"]
            end_date = data["order_end_date"]
            
            if isinstance(start_date, str):
                start_date = date.fromisoformat(start_date)
            if isinstance(end_date, str):
                end_date = date.fromisoformat(end_date)
            
            if start_date >= end_date:
                raise ValidationError(
                    detail="Order start date must be before end date",
                    error_code="INVALID_ORDER_DATES",
                    context={
                        "order_start_date": start_date.isoformat(),
                        "order_end_date": end_date.isoformat()
                    }
                )

    async def _validate_update_data(
        self,
        entity: Collection,
        data: Dict[str, Any],
        user_id: Optional[UUID]
    ) -> None:
        """Validate collection update data."""
        
        # Season validation
        if "season" in data and not await self._is_valid_season(data["season"]):
            raise ValidationError(
                detail=f"Invalid season: {data['season']}",
                error_code="INVALID_SEASON",
                context={"season": data["season"]}
            )
        
        # Year validation
        if "year" in data and not await self._is_valid_year(data["year"]):
            raise ValidationError(
                detail=f"Invalid year: {data['year']}",
                error_code="INVALID_YEAR",
                context={"year": data["year"]}
            )
        
        # Order dates validation
        start_date = data.get("order_start_date", entity.order_start_date)
        end_date = data.get("order_end_date", entity.order_end_date)
        
        if start_date and end_date:
            if isinstance(start_date, str):
                start_date = date.fromisoformat(start_date)
            if isinstance(end_date, str):
                end_date = date.fromisoformat(end_date)
            
            if start_date >= end_date:
                raise ValidationError(
                    detail="Order start date must be before end date",
                    error_code="INVALID_ORDER_DATES",
                    context={
                        "order_start_date": start_date.isoformat(),
                        "order_end_date": end_date.isoformat()
                    }
                )

    async def _check_create_conflicts(self, data: Dict[str, Any]) -> None:
        """Check for slug conflicts during creation."""
        if "slug" in data:
            slug_exists = await self.repository.check_slug_exists(data["slug"])
            if slug_exists:
                raise ConflictError(
                    detail=f"Collection with slug '{data['slug']}' already exists",
                    error_code="SLUG_ALREADY_EXISTS",
                    context={"slug": data["slug"]}
                )

    async def _check_update_conflicts(
        self,
        entity: Collection,
        data: Dict[str, Any]
    ) -> None:
        """Check for slug conflicts during update."""
        if "slug" in data and data["slug"] != entity.slug:
            slug_exists = await self.repository.check_slug_exists(
                data["slug"], exclude_id=entity.id
            )
            if slug_exists:
                raise ConflictError(
                    detail=f"Collection with slug '{data['slug']}' already exists",
                    error_code="SLUG_ALREADY_EXISTS",
                    context={"slug": data["slug"]}
                )

    async def _process_create_data(
        self,
        data: Dict[str, Any],
        user_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Process collection data before creation."""
        processed_data = data.copy()
        
        # Generate slug if not provided
        if not processed_data.get("slug"):
            processed_data["slug"] = self._generate_slug(
                processed_data["name"], processed_data["season"], processed_data["year"]
            )
        
        # Set default values
        processed_data.setdefault("is_published", False)
        processed_data.setdefault("status", "draft")
        
        return processed_data

    # Private Helper Methods

    async def _is_valid_season(self, season: str) -> bool:
        """Check if season is valid."""
        valid_seasons = ["Spring", "Summer", "Fall", "Winter", "Resort", "Pre-Fall"]
        return season in valid_seasons

    async def _is_valid_year(self, year: int) -> bool:
        """Check if year is valid."""
        current_year = date.today().year
        return 2020 <= year <= current_year + 5  # Allow up to 5 years in the future

    def _generate_slug(self, name: str, season: str, year: int) -> str:
        """Generate URL slug from collection name, season, and year."""
        # Combine name, season, and year
        base_slug = f"{name} {season} {year}"
        
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', base_slug.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        return slug