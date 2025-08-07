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

from app.models.product.product import Product
from app.models.product.variant import ProductVariant
from app.models.product.image import ProductImage
from app.models.product.technical_specification import TechnicalSpecification
from app.models.product.technical_drawing import TechnicalDrawing
from app.models.product.size_chart import SizeChart
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


class ProductVariantRepository(BaseRepository[ProductVariant]):
    """Repository for ProductVariant model."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(ProductVariant, db)
    
    async def get_by_product(
        self, 
        product_id: UUID,
        available_only: bool = False
    ) -> List[ProductVariant]:
        """Get variants for a product."""
        filters = [ProductVariant.product_id == product_id, ProductVariant.is_deleted == False]
        if available_only:
            filters.append(ProductVariant.is_available == True)
        
        query = (
            select(ProductVariant)
            .options(selectinload(ProductVariant.images))
            .where(and_(*filters))
            .order_by(ProductVariant.sort_order, ProductVariant.name)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_color(
        self, 
        product_id: UUID, 
        color: str
    ) -> Optional[ProductVariant]:
        """Get variant by product and color."""
        query = (
            select(ProductVariant)
            .options(selectinload(ProductVariant.images))
            .where(and_(
                ProductVariant.product_id == product_id,
                ProductVariant.color == color,
                ProductVariant.is_deleted == False
            ))
        )
        
        result = await self.db.execute(query)
        return result.scalars().first()


class ProductImageRepository(BaseRepository[ProductImage]):
    """Repository for ProductImage model."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(ProductImage, db)
    
    async def get_by_product(
        self, 
        product_id: UUID,
        image_type: Optional[str] = None
    ) -> List[ProductImage]:
        """Get images for a product."""
        filters = [ProductImage.product_id == product_id, ProductImage.is_deleted == False]
        if image_type:
            filters.append(ProductImage.type == image_type)
        
        query = (
            select(ProductImage)
            .where(and_(*filters))
            .order_by(ProductImage.sort_order, ProductImage.created_at)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_variant(
        self, 
        variant_id: UUID,
        image_type: Optional[str] = None
    ) -> List[ProductImage]:
        """Get images for a variant."""
        filters = [ProductImage.variant_id == variant_id, ProductImage.is_deleted == False]
        if image_type:
            filters.append(ProductImage.type == image_type)
        
        query = (
            select(ProductImage)
            .where(and_(*filters))
            .order_by(ProductImage.sort_order, ProductImage.created_at)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()


class TechnicalSpecificationRepository(BaseRepository[TechnicalSpecification]):
    """Repository for TechnicalSpecification model."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(TechnicalSpecification, db)
    
    async def get_by_product(
        self, 
        product_id: UUID,
        spec_type: Optional[str] = None
    ) -> List[TechnicalSpecification]:
        """Get technical specifications for a product."""
        filters = [TechnicalSpecification.product_id == product_id, TechnicalSpecification.is_deleted == False]
        if spec_type:
            filters.append(TechnicalSpecification.type == spec_type)
        
        query = (
            select(TechnicalSpecification)
            .where(and_(*filters))
            .order_by(TechnicalSpecification.sort_order, TechnicalSpecification.type)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()


class TechnicalDrawingRepository(BaseRepository[TechnicalDrawing]):
    """Repository for TechnicalDrawing model."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(TechnicalDrawing, db)
    
    async def get_by_product(
        self, 
        product_id: UUID,
        view: Optional[str] = None
    ) -> List[TechnicalDrawing]:
        """Get technical drawings for a product."""
        filters = [TechnicalDrawing.product_id == product_id, TechnicalDrawing.is_deleted == False]
        if view:
            filters.append(TechnicalDrawing.view == view)
        
        query = (
            select(TechnicalDrawing)
            .where(and_(*filters))
            .order_by(TechnicalDrawing.sort_order, TechnicalDrawing.view)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()


class SizeChartRepository(BaseRepository[SizeChart]):
    """Repository for SizeChart model."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(SizeChart, db)