"""
Collection Repository

Data access layer for Collection entity.
Pure data access operations without business logic.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection
from app.models.product.product import Product
from app.models.product.variant import ProductVariant
from app.repositories.base import BaseRepository


class CollectionRepository(BaseRepository[Collection]):
    """
    Collection repository with specialized data access methods.
    
    Handles collection-specific database queries and operations.
    """

    def __init__(self, db: AsyncSession):
        """Initialize with Collection model."""
        super().__init__(db, Collection)

    async def get_with_products(self, collection_id: UUID) -> Optional[Collection]:
        """
        Get collection with all its products loaded.
        
        Args:
            collection_id: Collection UUID
            
        Returns:
            Collection with products, or None if not found
        """
        query = (
            select(Collection)
            .options(
                selectinload(Collection.products)
                .selectinload(Product.variants)
                .selectinload(ProductVariant.images)
            )
            .where(and_(Collection.id == collection_id, Collection.is_deleted == False))
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Collection]:
        """
        Get collection by URL slug.
        
        Args:
            slug: Collection slug
            
        Returns:
            Collection or None if not found
        """
        return await self.get_by_field("slug", slug)

    async def get_published_collections(
        self,
        skip: int = 0,
        limit: int = 20,
        season: Optional[str] = None,
        year: Optional[int] = None,
        published_only: bool = True
    ) -> List[Collection]:
        """
        Get published collections with optional filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            season: Optional season filter
            year: Optional year filter
            published_only: Whether to only return published collections
            
        Returns:
            List of published collections
        """
        query = (
            select(Collection)
            .options(selectinload(Collection.products))
            .where(Collection.is_deleted == False)
        )
        
        # Apply filters
        if season:
            query = query.where(Collection.season == season)
        
        if year:
            query = query.where(Collection.year == year)
        
        if published_only:
            query = query.where(Collection.is_published == True)
        
        query = query.order_by(Collection.year.desc(), Collection.name)
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def check_slug_exists(self, slug: str, exclude_id: Optional[UUID] = None) -> bool:
        """
        Check if slug already exists.
        
        Args:
            slug: Slug to check
            exclude_id: Collection ID to exclude from check (for updates)
            
        Returns:
            True if slug exists, False otherwise
        """
        query = select(Collection).where(and_(
            Collection.slug == slug,
            Collection.is_deleted == False
        ))
        
        if exclude_id:
            query = query.where(Collection.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_featured_collections(self, limit: int = 6) -> List[Collection]:
        """
        Get featured collections (collections with featured products).
        
        Args:
            limit: Maximum number of collections to return
            
        Returns:
            List of collections with featured products
        """
        from app.models.product import Product
        
        query = (
            select(Collection)
            .options(selectinload(Collection.products))
            .join(Product, Collection.id == Product.collection_id)
            .where(and_(
                Collection.is_published == True,
                Collection.is_deleted == False,
                Product.is_featured == True,
                Product.status == "active",
                Product.is_deleted == False
            ))
            .distinct()
            .order_by(Collection.year.desc(), Collection.name)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_collections_with_stats(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> List[dict]:
        """
        Get collections with product counts and statistics.
        Useful for admin dashboard.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of dictionaries with collection data and stats
        """
        from sqlalchemy import func
        
        query = (
            select(
                Collection,
                func.count(Product.id).label('product_count'),
                func.count(
                    case((Product.status == 'active', Product.id), else_=None)
                ).label('active_product_count')
            )
            .outerjoin(Product, and_(
                Collection.id == Product.collection_id,
                Product.is_deleted == False
            ))
            .where(Collection.is_deleted == False)
            .group_by(Collection.id)
            .order_by(Collection.year.desc(), Collection.name)
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        
        collections_with_stats = []
        for row in result:
            collection = row[0]
            product_count = row[1]
            active_product_count = row[2]
            
            collections_with_stats.append({
                'collection': collection,
                'product_count': product_count,
                'active_product_count': active_product_count
            })
        
        return collections_with_stats

    async def search_collections(
        self,
        search_term: str,
        published_only: bool = True,
        skip: int = 0,
        limit: int = 20
    ) -> List[Collection]:
        """
        Search collections by name or description.
        
        Args:
            search_term: Text to search for
            published_only: Whether to only return published collections
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of matching collections
        """
        search_pattern = f"%{search_term}%"
        
        query = (
            select(Collection)
            .options(selectinload(Collection.products))
            .where(and_(
                Collection.is_deleted == False,
                or_(
                    Collection.name.ilike(search_pattern),
                    Collection.description.ilike(search_pattern)
                )
            ))
        )
        
        if published_only:
            query = query.where(Collection.is_published == True)
        
        query = (query
                .order_by(Collection.year.desc(), Collection.name)
                .offset(skip)
                .limit(limit))
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_season_year(
        self,
        season: str,
        year: int,
        published_only: bool = True
    ) -> List[Collection]:
        """
        Get collections by season and year.
        
        Args:
            season: Collection season
            year: Collection year
            published_only: Whether to only return published collections
            
        Returns:
            List of collections for the season/year
        """
        query = (
            select(Collection)
            .options(selectinload(Collection.products))
            .where(and_(
                Collection.season == season,
                Collection.year == year,
                Collection.is_deleted == False
            ))
        )
        
        if published_only:
            query = query.where(Collection.is_published == True)
        
        query = query.order_by(Collection.year.desc(), Collection.name)
        
        result = await self.db.execute(query)
        return result.scalars().all()