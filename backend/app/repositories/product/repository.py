"""
Product Repository

Data access layer for Product entity.
Contains only data access logic, no business rules.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.product_image import ProductImage
from app.models.technical_specification import TechnicalSpecification
from app.models.technical_drawing import TechnicalDrawing
from app.models.size_chart import SizeChart
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """
    Product repository with specialized data access methods.
    
    Inherits all standard CRUD operations from BaseRepository
    and adds product-specific queries.
    """

    def __init__(self, db: AsyncSession):
        """Initialize with Product model."""
        super().__init__(db, Product)

    async def get_with_full_details(self, product_id: UUID) -> Optional[Product]:
        """
        Get product with all related data for Virtual Showroom.
        
        Args:
            product_id: Product UUID
            
        Returns:
            Product with all relationships loaded, or None
        """
        query = (
            select(Product)
            .options(
                selectinload(Product.variants).selectinload(ProductVariant.images),
                selectinload(Product.images),
                selectinload(Product.specifications),
                selectinload(Product.technical_drawings),
                joinedload(Product.size_chart),
                joinedload(Product.collection)
            )
            .where(and_(Product.id == product_id, Product.is_deleted == False))
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_collection(
        self,
        collection_id: UUID,
        include_inactive: bool = False
    ) -> List[Product]:
        """
        Get all products in a collection.
        
        Args:
            collection_id: Collection UUID
            include_inactive: Whether to include inactive products
            
        Returns:
            List of products in the collection
        """
        query = (
            select(Product)
            .options(
                selectinload(Product.variants).selectinload(ProductVariant.images),
                selectinload(Product.images)
            )
            .where(and_(
                Product.collection_id == collection_id,
                Product.is_deleted == False
            ))
        )
        
        if not include_inactive:
            query = query.where(Product.status == "active")
        
        query = query.order_by(Product.name)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Get product by SKU.
        
        Args:
            sku: Product SKU
            
        Returns:
            Product or None if not found
        """
        return await self.get_by_field("sku", sku)

    async def search_products(
        self,
        search_term: str,
        category: Optional[str] = None,
        collection_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Product]:
        """
        Search products by name or description.
        
        Args:
            search_term: Text to search for
            category: Optional category filter
            collection_id: Optional collection filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of matching products
        """
        query = (
            select(Product)
            .options(
                selectinload(Product.variants).selectinload(ProductVariant.images),
                selectinload(Product.images)
            )
            .where(and_(
                Product.is_deleted == False,
                Product.status == "active"
            ))
        )
        
        # Text search
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.where(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.description.ilike(search_pattern),
                    Product.short_description.ilike(search_pattern)
                )
            )
        
        # Category filter
        if category:
            query = query.where(Product.category == category)
        
        # Collection filter
        if collection_id:
            query = query.where(Product.collection_id == collection_id)
        
        # Pagination and ordering
        query = query.order_by(Product.name).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_featured_products(self, limit: int = 10) -> List[Product]:
        """
        Get featured products.
        
        Args:
            limit: Maximum number of products to return
            
        Returns:
            List of featured products
        """
        query = (
            select(Product)
            .options(
                selectinload(Product.variants).selectinload(ProductVariant.images),
                selectinload(Product.images)
            )
            .where(and_(
                Product.is_featured == True,
                Product.status == "active",
                Product.is_deleted == False
            ))
            .order_by(Product.created_at.desc())
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Product]:
        """
        Get products by category.
        
        Args:
            category: Product category
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of products in category
        """
        query = (
            select(Product)
            .options(
                selectinload(Product.variants).selectinload(ProductVariant.images),
                selectinload(Product.images)
            )
            .where(and_(
                Product.category == category,
                Product.status == "active",
                Product.is_deleted == False
            ))
            .order_by(Product.name)
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def check_sku_exists(self, sku: str, exclude_id: Optional[UUID] = None) -> bool:
        """
        Check if SKU already exists.
        
        Args:
            sku: SKU to check
            exclude_id: Product ID to exclude from check (for updates)
            
        Returns:
            True if SKU exists, False otherwise
        """
        query = select(Product).where(and_(
            Product.sku == sku,
            Product.is_deleted == False
        ))
        
        if exclude_id:
            query = query.where(Product.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_products_needing_images(self) -> List[Product]:
        """
        Get products that don't have any images.
        Useful for data quality checks.
        
        Returns:
            List of products without images
        """
        query = (
            select(Product)
            .outerjoin(ProductImage)
            .where(and_(
                Product.is_deleted == False,
                ProductImage.id.is_(None)
            ))
            .order_by(Product.created_at.desc())
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()