"""
Collection Service

Business logic for Collection entity.
Handles collection operations, validation, and business rules.
"""

import re
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection
from app.repositories.collection import CollectionRepository
from app.services.base import BaseService
from app.core.exceptions import ValidationError, ConflictError, NotFoundError
from app.schemas.collection import (
    CollectionCreate, CollectionUpdate, CollectionResponse,
    CollectionListFilters, CollectionAnalytics
)


class CollectionService(BaseService[Collection, CollectionRepository]):
    """
    Collection service with business logic and validation.
    """

    def __init__(self, db: AsyncSession):
        """Initialize collection service."""
        super().__init__(db, CollectionRepository, Collection)

    async def create_collection(
        self, 
        data: CollectionCreate, 
        user_id: Optional[UUID] = None
    ) -> Collection:
        """
        Create a new collection with business validation.
        
        Args:
            data: Collection creation data
            user_id: ID of creating user
            
        Returns:
            Created collection
        """
        # Convert to dict for processing
        collection_data = data.model_dump(exclude_unset=True)
        
        # Generate slug if not provided
        if not collection_data.get('slug'):
            collection_data['slug'] = await self._generate_unique_slug(collection_data['name'])
        
        # Validate and process data
        await self._validate_create_data(collection_data, user_id)
        await self._check_create_conflicts(collection_data)
        
        # Process data
        processed_data = await self._process_create_data(collection_data, user_id)
        
        # Create collection
        collection = await self.repository.create(processed_data, user_id)
        
        # Post-creation actions
        await self._post_create_actions(collection, user_id)
        
        return collection

    async def update_collection(
        self,
        collection_id: UUID,
        data: CollectionUpdate,
        user_id: Optional[UUID] = None
    ) -> Collection:
        """
        Update an existing collection.
        
        Args:
            collection_id: Collection UUID
            data: Update data
            user_id: ID of updating user
            
        Returns:
            Updated collection
        """
        # Get existing collection
        existing = await self.repository.get_by_id(collection_id)
        if not existing:
            raise NotFoundError(
                detail=f"Collection with ID {collection_id} not found",
                error_code="COLLECTION_NOT_FOUND"
            )
        
        # Convert to dict for processing
        update_data = data.model_dump(exclude_unset=True)
        
        if not update_data:
            return existing
        
        # Validate and process data
        await self._validate_update_data(existing, update_data, user_id)
        await self._check_update_conflicts(existing, update_data)
        
        # Process data
        processed_data = await self._process_update_data(existing, update_data, user_id)
        
        # Update collection
        updated_collection = await self.repository.update(collection_id, processed_data, user_id)
        
        # Post-update actions
        await self._post_update_actions(existing, updated_collection, user_id)
        
        return updated_collection

    async def get_collection_by_slug(self, slug: str) -> Collection:
        """
        Get collection by slug.
        
        Args:
            slug: Collection slug
            
        Returns:
            Collection
        """
        collection = await self.repository.get_by_slug(slug)
        if not collection:
            raise NotFoundError(
                detail=f"Collection with slug '{slug}' not found",
                error_code="COLLECTION_NOT_FOUND"
            )
        return collection

    async def list_collections(
        self,
        filters: CollectionListFilters,
        skip: int = 0,
        limit: int = 20,
        user_id: Optional[UUID] = None
    ) -> Tuple[List[Collection], int]:
        """
        List collections with filtering and pagination.
        
        Args:
            filters: Filter parameters
            skip: Number of records to skip
            limit: Maximum records to return
            user_id: ID of requesting user
            
        Returns:
            Tuple of (collections, total_count)
        """
        # Convert filters to dict
        filter_dict = filters.model_dump(exclude_unset=True)
        
        # Apply business logic filters
        business_filters = await self._apply_business_filters(filter_dict, user_id)
        
        # Get collections using repository
        collections = await self.repository.get_collections_by_filters(
            business_filters, skip, limit
        )
        
        # Get total count
        total = await self.repository.count(filters=business_filters)
        
        return collections, total

    async def publish_collection(
        self,
        collection_id: UUID,
        publish: bool = True,
        user_id: Optional[UUID] = None
    ) -> Collection:
        """
        Publish or unpublish a collection.
        
        Args:
            collection_id: Collection UUID
            publish: Whether to publish (True) or unpublish (False)
            user_id: ID of user performing action
            
        Returns:
            Updated collection
        """
        collection = await self.repository.get_by_id(collection_id)
        if not collection:
            raise NotFoundError(
                detail=f"Collection with ID {collection_id} not found",
                error_code="COLLECTION_NOT_FOUND"
            )
        
        # Check permissions
        await self._check_publish_permission(collection, user_id)
        
        # Validate publication requirements
        if publish:
            await self._validate_publication_requirements(collection)
        
        # Update publication status
        update_data = {
            "is_published": publish,
            "status": "active" if publish else "draft"
        }
        
        updated_collection = await self.repository.update(collection_id, update_data, user_id)
        
        # Post-publication actions
        await self._post_publication_actions(updated_collection, publish, user_id)
        
        return updated_collection

    async def get_collection_analytics(self, collection_id: UUID) -> CollectionAnalytics:
        """
        Get analytics data for a collection.
        
        Args:
            collection_id: Collection UUID
            
        Returns:
            Collection analytics
        """
        collection = await self.repository.get_by_id(collection_id)
        if not collection:
            raise NotFoundError(
                detail=f"Collection with ID {collection_id} not found",
                error_code="COLLECTION_NOT_FOUND"
            )
        
        # Get analytics data from repository
        analytics_data = await self.repository.get_collection_analytics(collection_id)
        
        # Calculate completion percentage
        completion_percentage = await self._calculate_completion_percentage(collection)
        
        # Calculate popularity score
        popularity_score = await self._calculate_popularity_score(collection, analytics_data)
        
        return CollectionAnalytics(
            collection_id=collection_id,
            collection_name=collection.name,
            collection_slug=collection.slug,
            total_products=analytics_data.get('total_products', 0),
            product_categories=analytics_data.get('products_by_category', {}),
            average_product_price=analytics_data.get('average_price'),
            price_range=analytics_data.get('price_range', {}),
            total_variants=analytics_data.get('total_variants', 0),
            total_images=analytics_data.get('total_images', 0),
            creation_timeline=[],  # Would be populated with time series data
            popularity_score=popularity_score,
            completion_percentage=completion_percentage
        )

    async def search_collections(
        self,
        query: str,
        published_only: bool = True,
        skip: int = 0,
        limit: int = 20
    ) -> List[Collection]:
        """
        Search collections by text query.
        
        Args:
            query: Search query
            published_only: Whether to only search published collections
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of matching collections
        """
        if not query or len(query.strip()) < 2:
            raise ValidationError(
                detail="Search query must be at least 2 characters long",
                error_code="INVALID_SEARCH_QUERY"
            )
        
        return await self.repository.search_collections(
            query.strip(), published_only, skip, limit
        )

    async def get_featured_collections(self, limit: int = 6) -> List[Collection]:
        """
        Get featured collections.
        
        Args:
            limit: Maximum number of collections to return
            
        Returns:
            List of featured collections
        """
        return await self.repository.get_featured_collections(limit)

    # Business Logic Helpers

    async def _validate_create_data(
        self,
        data: Dict[str, Any],
        user_id: Optional[UUID]
    ) -> None:
        """Validate collection creation data."""
        # Validate season/year combination
        await self._validate_season_year_combination(data)
        
        # Validate order dates
        await self._validate_order_dates(data)
        
        # Validate SEO fields
        await self._validate_seo_fields(data)

    async def _validate_update_data(
        self,
        collection: Collection,
        data: Dict[str, Any],
        user_id: Optional[UUID]
    ) -> None:
        """Validate collection update data."""
        # Only validate fields that are being updated
        if 'season' in data or 'year' in data:
            season = data.get('season', collection.season)
            year = data.get('year', collection.year)
            await self._validate_season_year_combination({'season': season, 'year': year})
        
        if 'order_start_date' in data or 'order_end_date' in data:
            await self._validate_order_dates(data, collection)

    async def _check_create_conflicts(self, data: Dict[str, Any]) -> None:
        """Check for conflicts during creation."""
        # Check slug uniqueness
        if await self.repository.check_slug_exists(data['slug']):
            raise ConflictError(
                detail=f"Collection with slug '{data['slug']}' already exists",
                error_code="SLUG_ALREADY_EXISTS"
            )

    async def _check_update_conflicts(
        self,
        collection: Collection,
        data: Dict[str, Any]
    ) -> None:
        """Check for conflicts during update."""
        # Check slug uniqueness if slug is being updated
        if 'slug' in data and data['slug'] != collection.slug:
            if await self.repository.check_slug_exists(data['slug'], collection.id):
                raise ConflictError(
                    detail=f"Collection with slug '{data['slug']}' already exists",
                    error_code="SLUG_ALREADY_EXISTS"
                )

    async def _process_create_data(
        self,
        data: Dict[str, Any],
        user_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Process data before creation."""
        # Ensure slug is URL-friendly
        if 'slug' in data:
            data['slug'] = self._normalize_slug(data['slug'])
        
        # Set default metadata
        if 'metadata' not in data:
            data['metadata'] = {}
        
        # Add creation metadata
        data['metadata']['created_by_service'] = True
        data['metadata']['creation_source'] = 'api'
        
        return data

    async def _process_update_data(
        self,
        collection: Collection,
        data: Dict[str, Any],
        user_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Process data before update."""
        # Normalize slug if being updated
        if 'slug' in data:
            data['slug'] = self._normalize_slug(data['slug'])
        
        # Update metadata
        if 'metadata' in data:
            # Merge with existing metadata
            existing_metadata = collection.metadata or {}
            data['metadata'] = {**existing_metadata, **data['metadata']}
        
        return data

    async def _generate_unique_slug(self, name: str) -> str:
        """Generate a unique slug from collection name."""
        # Convert to slug format
        base_slug = self._normalize_slug(name)
        
        # Check if slug is unique
        if not await self.repository.check_slug_exists(base_slug):
            return base_slug
        
        # If not unique, append number
        counter = 1
        while True:
            candidate_slug = f"{base_slug}-{counter}"
            if not await self.repository.check_slug_exists(candidate_slug):
                return candidate_slug
            counter += 1

    def _normalize_slug(self, text: str) -> str:
        """Normalize text to URL-friendly slug."""
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[\s_-]+', '-', slug)
        slug = slug.strip('-')
        
        # Ensure it's not empty
        if not slug:
            slug = 'collection'
        
        return slug

    async def _validate_season_year_combination(self, data: Dict[str, Any]) -> None:
        """Validate season and year combination."""
        year = data.get('year')
        if year and year < 2020:
            raise ValidationError(
                detail="Collection year cannot be before 2020",
                error_code="INVALID_YEAR"
            )
        
        if year and year > datetime.now().year + 2:
            raise ValidationError(
                detail=f"Collection year cannot be more than 2 years in the future",
                error_code="INVALID_YEAR"
            )

    async def _validate_order_dates(
        self,
        data: Dict[str, Any],
        existing: Optional[Collection] = None
    ) -> None:
        """Validate order period dates."""
        start_date = data.get('order_start_date')
        end_date = data.get('order_end_date')
        
        # Use existing values if not provided in update
        if existing:
            start_date = start_date or existing.order_start_date
            end_date = end_date or existing.order_end_date
        
        if start_date and end_date:
            if end_date <= start_date:
                raise ValidationError(
                    detail="Order end date must be after start date",
                    error_code="INVALID_ORDER_DATES"
                )

    async def _validate_seo_fields(self, data: Dict[str, Any]) -> None:
        """Validate SEO fields."""
        seo_title = data.get('seo_title')
        if seo_title and len(seo_title) > 60:
            raise ValidationError(
                detail="SEO title should be 60 characters or less for optimal results",
                error_code="SEO_TITLE_TOO_LONG"
            )
        
        seo_description = data.get('seo_description')
        if seo_description and (len(seo_description) < 120 or len(seo_description) > 160):
            raise ValidationError(
                detail="SEO description should be between 120-160 characters for optimal results",
                error_code="SEO_DESCRIPTION_INVALID_LENGTH"
            )

    async def _check_publish_permission(
        self,
        collection: Collection,
        user_id: Optional[UUID]
    ) -> None:
        """Check if user can publish collection."""
        # This would typically check user roles/permissions
        # For now, assume all authenticated users can publish
        pass

    async def _validate_publication_requirements(self, collection: Collection) -> None:
        """Validate that collection meets publication requirements."""
        # Check if collection has required fields
        if not collection.description:
            raise ValidationError(
                detail="Collection must have a description before publishing",
                error_code="MISSING_DESCRIPTION"
            )
        
        # Check if collection has products
        # This would require querying products - simplified for now
        pass

    async def _calculate_completion_percentage(self, collection: Collection) -> float:
        """Calculate how complete the collection data is."""
        total_fields = 10  # Total number of important fields
        completed_fields = 0
        
        # Count completed fields
        if collection.name:
            completed_fields += 1
        if collection.description:
            completed_fields += 1
        if collection.short_description:
            completed_fields += 1
        if collection.seo_title:
            completed_fields += 1
        if collection.seo_description:
            completed_fields += 1
        if collection.order_start_date:
            completed_fields += 1
        if collection.order_end_date:
            completed_fields += 1
        
        # Additional checks would go here (products, images, etc.)
        completed_fields += 3  # Placeholder for other checks
        
        return (completed_fields / total_fields) * 100

    async def _calculate_popularity_score(
        self,
        collection: Collection,
        analytics_data: Dict[str, Any]
    ) -> float:
        """Calculate collection popularity score."""
        score = 0.0
        
        # Base score from number of products
        product_count = analytics_data.get('total_products', 0)
        score += min(product_count * 0.1, 1.0)  # Max 1.0 from products
        
        # Score from publication status
        if collection.is_published:
            score += 0.5
        
        # Score from having complete data
        if collection.description and collection.seo_title:
            score += 0.3
        
        # Score from recent activity (simplified)
        if collection.updated_at and collection.updated_at > datetime.utcnow().replace(day=1):
            score += 0.2
        
        return min(score, 5.0)  # Max score of 5.0

    async def _post_create_actions(
        self,
        collection: Collection,
        user_id: Optional[UUID]
    ) -> None:
        """Post-creation business logic."""
        # This could include:
        # - Sending notifications
        # - Creating audit logs
        # - Setting up default configurations
        pass

    async def _post_update_actions(
        self,
        old_collection: Collection,
        new_collection: Collection,
        user_id: Optional[UUID]
    ) -> None:
        """Post-update business logic."""
        # This could include:
        # - Invalidating caches
        # - Sending notifications for significant changes
        # - Creating audit logs
        pass

    async def _post_publication_actions(
        self,
        collection: Collection,
        published: bool,
        user_id: Optional[UUID]
    ) -> None:
        """Post-publication business logic."""
        # This could include:
        # - Sending notifications
        # - Updating search indexes
        # - Creating audit logs
        pass

    async def _apply_business_filters(
        self,
        filters: Optional[Dict[str, Any]],
        user_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Apply business logic filters."""
        if not filters:
            filters = {}
        
        # Non-admin users should only see published collections
        # This would check user role in a real implementation
        if user_id:  # Simplified - assume logged in users see all
            pass
        else:
            filters['is_published'] = True
        
        return filters