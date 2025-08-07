"""
Product Service

Business logic for Product entity and related models.
Handles product operations, validation, and business rules.
"""

import re
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product.product import Product
from app.models.product.variant import ProductVariant
from app.models.product.image import ProductImage
from app.models.product.technical_specification import TechnicalSpecification
from app.models.product.size_chart import SizeChart
from app.repositories.product.repository import (
    ProductRepository, ProductVariantRepository, ProductImageRepository,
    TechnicalSpecificationRepository, SizeChartRepository
)
from app.repositories.collection import CollectionRepository
from app.services.base import BaseService
from app.core.exceptions import ValidationError, ConflictError, NotFoundError, BadRequestError
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductVariantCreate, ProductVariantUpdate,
    ProductImageCreate, ProductImageUpdate,
    TechnicalSpecificationCreate, TechnicalSpecificationUpdate,
    SizeChartCreate, SizeChartUpdate,
    ProductListFilters, ProductAnalytics
)


class ProductService(BaseService[Product, ProductRepository]):
    """
    Product service with business logic and validation.
    """

    def __init__(self, db: AsyncSession):
        """Initialize product service."""
        super().__init__(db, ProductRepository, Product)
        self.variant_repository = ProductVariantRepository(db)
        self.image_repository = ProductImageRepository(db)
        self.spec_repository = TechnicalSpecificationRepository(db)
        self.size_chart_repository = SizeChartRepository(db)
        self.collection_repository = CollectionRepository(db)

    async def create_product_with_variants(
        self,
        data: ProductCreate,
        user_id: Optional[UUID] = None
    ) -> Product:
        """
        Create a new product with variants and related data.
        
        Args:
            data: Product creation data including variants
            user_id: ID of creating user
            
        Returns:
            Created product with all relationships
        """
        # Start transaction
        async with self.db.begin():
            # Validate collection exists
            collection = await self.collection_repository.get_by_id(data.collection_id)
            if not collection:
                raise ValidationError(
                    detail=f"Collection with ID {data.collection_id} not found",
                    error_code="COLLECTION_NOT_FOUND"
                )
            
            # Convert to dict for processing
            product_data = data.model_dump(exclude={'variants', 'specifications', 'size_chart'})
            
            # Validate and process main product data
            await self._validate_create_data(product_data, user_id)
            await self._check_create_conflicts(product_data)
            
            # Process main product data
            processed_data = await self._process_create_data(product_data, user_id)
            
            # Create main product
            product = await self.repository.create(processed_data, user_id)
            
            # Create variants if provided
            if data.variants:
                await self._create_product_variants(product.id, data.variants, user_id)
            
            # Create specifications if provided
            if data.specifications:
                await self._create_technical_specifications(product.id, data.specifications, user_id)
            
            # Create size chart if provided
            if data.size_chart:
                await self._create_size_chart(product.id, data.size_chart, user_id)
            
            # Post-creation actions
            await self._post_create_actions(product, user_id)
            
            # Return product with all relationships loaded
            return await self.repository.get_with_full_details(product.id)

    async def update_product(
        self,
        product_id: UUID,
        data: ProductUpdate,
        user_id: Optional[UUID] = None
    ) -> Product:
        """
        Update an existing product.
        
        Args:
            product_id: Product UUID
            data: Update data
            user_id: ID of updating user
            
        Returns:
            Updated product
        """
        # Get existing product
        existing = await self.repository.get_by_id(product_id)
        if not existing:
            raise NotFoundError(
                detail=f"Product with ID {product_id} not found",
                error_code="PRODUCT_NOT_FOUND"
            )
        
        # Convert to dict for processing
        update_data = data.model_dump(exclude_unset=True)
        
        if not update_data:
            return existing
        
        # Validate collection if being updated
        if 'collection_id' in update_data:
            collection = await self.collection_repository.get_by_id(update_data['collection_id'])
            if not collection:
                raise ValidationError(
                    detail=f"Collection with ID {update_data['collection_id']} not found",
                    error_code="COLLECTION_NOT_FOUND"
                )
        
        # Validate and process data
        await self._validate_update_data(existing, update_data, user_id)
        await self._check_update_conflicts(existing, update_data)
        
        # Process data
        processed_data = await self._process_update_data(existing, update_data, user_id)
        
        # Update product
        updated_product = await self.repository.update(product_id, processed_data, user_id)
        
        # Post-update actions
        await self._post_update_actions(existing, updated_product, user_id)
        
        return updated_product

    async def get_product_with_details(self, product_id: UUID) -> Product:
        """
        Get product with all details for Virtual Showroom.
        
        Args:
            product_id: Product UUID
            
        Returns:
            Product with all relationships loaded
        """
        product = await self.repository.get_with_full_details(product_id)
        if not product:
            raise NotFoundError(
                detail=f"Product with ID {product_id} not found",
                error_code="PRODUCT_NOT_FOUND"
            )
        return product

    async def get_product_by_sku(self, sku: str) -> Product:
        """
        Get product by SKU.
        
        Args:
            sku: Product SKU
            
        Returns:
            Product
        """
        product = await self.repository.get_by_sku(sku.upper())
        if not product:
            raise NotFoundError(
                detail=f"Product with SKU '{sku}' not found",
                error_code="PRODUCT_NOT_FOUND"
            )
        return product

    async def list_products(
        self,
        filters: ProductListFilters,
        skip: int = 0,
        limit: int = 20,
        order_by: Optional[str] = None,
        user_id: Optional[UUID] = None
    ) -> Tuple[List[Product], int]:
        """
        List products with filtering and pagination.
        
        Args:
            filters: Filter parameters
            skip: Number of records to skip
            limit: Maximum records to return
            order_by: Field to order by
            user_id: ID of requesting user
            
        Returns:
            Tuple of (products, total_count)
        """
        # Convert filters to dict
        filter_dict = filters.model_dump(exclude_unset=True)
        
        # Apply business logic filters
        business_filters = await self._apply_business_filters(filter_dict, user_id)
        
        # Get products and count from repository
        products, total = await self.repository.get_products_with_filters(
            business_filters, skip, limit, order_by
        )
        
        return products, total

    async def search_products(
        self,
        query: str,
        category: Optional[str] = None,
        collection_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Product]:
        """
        Search products by text query.
        
        Args:
            query: Search query
            category: Optional category filter
            collection_id: Optional collection filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of matching products
        """
        if not query or len(query.strip()) < 2:
            raise ValidationError(
                detail="Search query must be at least 2 characters long",
                error_code="INVALID_SEARCH_QUERY"
            )
        
        return await self.repository.search_products(
            query.strip(), category, collection_id, "active", skip, limit
        )

    async def get_featured_products(self, limit: int = 10) -> List[Product]:
        """
        Get featured products.
        
        Args:
            limit: Maximum number of products to return
            
        Returns:
            List of featured products
        """
        return await self.repository.get_featured_products(limit)

    async def get_products_by_collection(
        self,
        collection_id: UUID,
        include_inactive: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> List[Product]:
        """
        Get all products in a collection.
        
        Args:
            collection_id: Collection UUID
            include_inactive: Whether to include inactive products
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of products in the collection
        """
        # Validate collection exists
        collection = await self.collection_repository.get_by_id(collection_id)
        if not collection:
            raise NotFoundError(
                detail=f"Collection with ID {collection_id} not found",
                error_code="COLLECTION_NOT_FOUND"
            )
        
        return await self.repository.get_by_collection(
            collection_id, include_inactive, skip, limit
        )

    async def update_product_status(
        self,
        product_id: UUID,
        status: str,
        user_id: Optional[UUID] = None
    ) -> Product:
        """
        Update product status.
        
        Args:
            product_id: Product UUID
            status: New status
            user_id: ID of user performing update
            
        Returns:
            Updated product
        """
        # Validate status
        valid_statuses = ["active", "discontinued", "coming_soon"]
        if status not in valid_statuses:
            raise ValidationError(
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                error_code="INVALID_STATUS"
            )
        
        # Update status
        return await self.update_product(
            product_id,
            ProductUpdate(status=status),
            user_id
        )

    async def toggle_featured_status(
        self,
        product_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Product:
        """
        Toggle product featured status.
        
        Args:
            product_id: Product UUID
            user_id: ID of user performing update
            
        Returns:
            Updated product
        """
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise NotFoundError(
                detail=f"Product with ID {product_id} not found",
                error_code="PRODUCT_NOT_FOUND"
            )
        
        return await self.update_product(
            product_id,
            ProductUpdate(is_featured=not product.is_featured),
            user_id
        )

    async def get_product_analytics(self, product_id: UUID) -> ProductAnalytics:
        """
        Get analytics data for a product.
        
        Args:
            product_id: Product UUID
            
        Returns:
            Product analytics
        """
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise NotFoundError(
                detail=f"Product with ID {product_id} not found",
                error_code="PRODUCT_NOT_FOUND"
            )
        
        # Get analytics data from repository
        analytics_data = await self.repository.get_product_analytics(product_id)
        
        return ProductAnalytics(
            total_variants=analytics_data.get('total_variants', 0),
            total_images=analytics_data.get('total_images', 0),
            variants_by_color=analytics_data.get('variants_by_color', {}),
            average_price=product.retail_price,
            specifications_count=analytics_data.get('specifications_count', 0),
            has_size_chart=analytics_data.get('has_size_chart', False)
        )

    # Variant Management

    async def add_product_variant(
        self,
        product_id: UUID,
        variant_data: ProductVariantCreate,
        user_id: Optional[UUID] = None
    ) -> ProductVariant:
        """
        Add a new variant to a product.
        
        Args:
            product_id: Product UUID
            variant_data: Variant creation data
            user_id: ID of creating user
            
        Returns:
            Created variant
        """
        # Validate product exists
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise NotFoundError(
                detail=f"Product with ID {product_id} not found",
                error_code="PRODUCT_NOT_FOUND"
            )
        
        # Prepare variant data
        data = variant_data.model_dump()
        data['product_id'] = product_id
        
        # Generate full SKU
        data['sku'] = f"{product.sku}-{variant_data.sku_suffix}"
        
        # Validate SKU uniqueness
        await self._validate_variant_sku_unique(data['sku'])
        
        # Create variant
        return await self.variant_repository.create(data, user_id)

    async def update_product_variant(
        self,
        variant_id: UUID,
        variant_data: ProductVariantUpdate,
        user_id: Optional[UUID] = None
    ) -> ProductVariant:
        """
        Update a product variant.
        
        Args:
            variant_id: Variant UUID
            variant_data: Update data
            user_id: ID of updating user
            
        Returns:
            Updated variant
        """
        update_data = variant_data.model_dump(exclude_unset=True)
        
        # If sku_suffix is being updated, regenerate full SKU
        if 'sku_suffix' in update_data:
            variant = await self.variant_repository.get_by_id(variant_id)
            if variant:
                product = await self.repository.get_by_id(variant.product_id)
                if product:
                    new_sku = f"{product.sku}-{update_data['sku_suffix']}"
                    await self._validate_variant_sku_unique(new_sku, variant_id)
                    update_data['sku'] = new_sku
        
        updated_variant = await self.variant_repository.update(variant_id, update_data, user_id)
        if not updated_variant:
            raise NotFoundError(
                detail=f"Product variant with ID {variant_id} not found",
                error_code="VARIANT_NOT_FOUND"
            )
        
        return updated_variant

    # Image Management

    async def add_product_image(
        self,
        product_id: UUID,
        image_data: ProductImageCreate,
        user_id: Optional[UUID] = None
    ) -> ProductImage:
        """
        Add an image to a product.
        
        Args:
            product_id: Product UUID
            image_data: Image data
            user_id: ID of creating user
            
        Returns:
            Created image record
        """
        # Validate product exists
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise NotFoundError(
                detail=f"Product with ID {product_id} not found",
                error_code="PRODUCT_NOT_FOUND"
            )
        
        # Validate variant exists if specified
        if image_data.variant_id:
            variant = await self.variant_repository.get_by_id(image_data.variant_id)
            if not variant or variant.product_id != product_id:
                raise ValidationError(
                    detail="Variant does not belong to the specified product",
                    error_code="INVALID_VARIANT"
                )
        
        # Prepare image data
        data = image_data.model_dump()
        data['product_id'] = product_id
        
        # Create image record
        return await self.image_repository.create(data, user_id)

    # Technical Specifications Management

    async def add_technical_specification(
        self,
        product_id: UUID,
        spec_data: TechnicalSpecificationCreate,
        user_id: Optional[UUID] = None
    ) -> TechnicalSpecification:
        """
        Add a technical specification to a product.
        
        Args:
            product_id: Product UUID
            spec_data: Specification data
            user_id: ID of creating user
            
        Returns:
            Created specification
        """
        # Validate product exists
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise NotFoundError(
                detail=f"Product with ID {product_id} not found",
                error_code="PRODUCT_NOT_FOUND"
            )
        
        # Prepare specification data
        data = spec_data.model_dump()
        data['product_id'] = product_id
        
        # Create specification
        return await self.spec_repository.create(data, user_id)

    # Size Chart Management

    async def create_size_chart(
        self,
        product_id: UUID,
        size_chart_data: SizeChartCreate,
        user_id: Optional[UUID] = None
    ) -> SizeChart:
        """
        Create a size chart for a product.
        
        Args:
            product_id: Product UUID
            size_chart_data: Size chart data
            user_id: ID of creating user
            
        Returns:
            Created size chart
        """
        # Validate product exists
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise NotFoundError(
                detail=f"Product with ID {product_id} not found",
                error_code="PRODUCT_NOT_FOUND"
            )
        
        # Check if product already has a size chart
        existing_chart = await self.size_chart_repository.get_by_product(product_id)
        if existing_chart:
            raise ConflictError(
                detail="Product already has a size chart",
                error_code="SIZE_CHART_EXISTS"
            )
        
        # Prepare size chart data
        data = size_chart_data.model_dump()
        data['product_id'] = product_id
        
        # Create size chart
        return await self.size_chart_repository.create(data, user_id)

    # Business Logic Helpers

    async def _validate_create_data(
        self,
        data: Dict[str, Any],
        user_id: Optional[UUID]
    ) -> None:
        """Validate product creation data."""
        # Validate SKU format
        await self._validate_sku_format(data.get('sku', ''))
        
        # Validate prices
        await self._validate_prices(data)
        
        # Validate category
        await self._validate_category(data.get('category', ''))

    async def _validate_update_data(
        self,
        product: Product,
        data: Dict[str, Any],
        user_id: Optional[UUID]
    ) -> None:
        """Validate product update data."""
        if 'sku' in data:
            await self._validate_sku_format(data['sku'])
        
        if 'retail_price' in data or 'wholesale_price' in data:
            await self._validate_prices(data, product)
        
        if 'category' in data:
            await self._validate_category(data['category'])

    async def _check_create_conflicts(self, data: Dict[str, Any]) -> None:
        """Check for conflicts during creation."""
        # Check SKU uniqueness
        if await self.repository.check_sku_exists(data['sku']):
            raise ConflictError(
                detail=f"Product with SKU '{data['sku']}' already exists",
                error_code="SKU_ALREADY_EXISTS"
            )

    async def _check_update_conflicts(
        self,
        product: Product,
        data: Dict[str, Any]
    ) -> None:
        """Check for conflicts during update."""
        # Check SKU uniqueness if SKU is being updated
        if 'sku' in data and data['sku'] != product.sku:
            if await self.repository.check_sku_exists(data['sku'], product.id):
                raise ConflictError(
                    detail=f"Product with SKU '{data['sku']}' already exists",
                    error_code="SKU_ALREADY_EXISTS"
                )

    async def _process_create_data(
        self,
        data: Dict[str, Any],
        user_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Process data before creation."""
        # Ensure SKU is uppercase
        if 'sku' in data:
            data['sku'] = data['sku'].upper()
        
        # Ensure currency is uppercase
        if 'currency' in data:
            data['currency'] = data['currency'].upper()
        
        # Set default metadata
        if 'metadata' not in data:
            data['metadata'] = {}
        
        return data

    async def _process_update_data(
        self,
        product: Product,
        data: Dict[str, Any],
        user_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Process data before update."""
        # Ensure SKU is uppercase if being updated
        if 'sku' in data:
            data['sku'] = data['sku'].upper()
        
        # Ensure currency is uppercase if being updated
        if 'currency' in data:
            data['currency'] = data['currency'].upper()
        
        return data

    def _validate_sku_format(self, sku: str) -> None:
        """Validate SKU format."""
        if not sku:
            raise ValidationError(
                detail="SKU is required",
                error_code="SKU_REQUIRED"
            )
        
        if not re.match(r'^[A-Z0-9\-_]+$', sku.upper()):
            raise ValidationError(
                detail="SKU must contain only letters, numbers, hyphens, and underscores",
                error_code="INVALID_SKU_FORMAT"
            )
        
        if len(sku) < 3 or len(sku) > 50:
            raise ValidationError(
                detail="SKU must be between 3 and 50 characters long",
                error_code="INVALID_SKU_LENGTH"
            )

    async def _validate_prices(
        self,
        data: Dict[str, Any],
        existing: Optional[Product] = None
    ) -> None:
        """Validate product prices."""
        retail_price = data.get('retail_price')
        wholesale_price = data.get('wholesale_price')
        
        # Use existing prices if not provided in update
        if existing:
            retail_price = retail_price if retail_price is not None else existing.retail_price
            wholesale_price = wholesale_price if wholesale_price is not None else existing.wholesale_price
        
        if retail_price and retail_price < 0:
            raise ValidationError(
                detail="Retail price cannot be negative",
                error_code="INVALID_RETAIL_PRICE"
            )
        
        if wholesale_price and wholesale_price < 0:
            raise ValidationError(
                detail="Wholesale price cannot be negative",
                error_code="INVALID_WHOLESALE_PRICE"
            )
        
        if retail_price and wholesale_price and wholesale_price >= retail_price:
            raise ValidationError(
                detail="Wholesale price must be less than retail price",
                error_code="WHOLESALE_PRICE_TOO_HIGH"
            )

    def _validate_category(self, category: str) -> None:
        """Validate product category."""
        valid_categories = ["bikini", "one-piece", "accessory", "cover-up"]
        if category not in valid_categories:
            raise ValidationError(
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}",
                error_code="INVALID_CATEGORY"
            )

    async def _validate_variant_sku_unique(
        self,
        sku: str,
        exclude_id: Optional[UUID] = None
    ) -> None:
        """Validate that variant SKU is unique."""
        # This would check against a variant SKU table/field
        # For now, simplified validation
        pass

    async def _create_product_variants(
        self,
        product_id: UUID,
        variants_data: List[ProductVariantCreate],
        user_id: Optional[UUID]
    ) -> List[ProductVariant]:
        """Create product variants."""
        created_variants = []
        
        for variant_data in variants_data:
            variant = await self.add_product_variant(product_id, variant_data, user_id)
            created_variants.append(variant)
        
        return created_variants

    async def _create_technical_specifications(
        self,
        product_id: UUID,
        specs_data: List[TechnicalSpecificationCreate],
        user_id: Optional[UUID]
    ) -> List[TechnicalSpecification]:
        """Create technical specifications."""
        created_specs = []
        
        for spec_data in specs_data:
            spec = await self.add_technical_specification(product_id, spec_data, user_id)
            created_specs.append(spec)
        
        return created_specs

    async def _create_size_chart(
        self,
        product_id: UUID,
        size_chart_data: SizeChartCreate,
        user_id: Optional[UUID]
    ) -> SizeChart:
        """Create size chart for product."""
        return await self.create_size_chart(product_id, size_chart_data, user_id)

    async def _apply_business_filters(
        self,
        filters: Optional[Dict[str, Any]],
        user_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Apply business logic filters."""
        if not filters:
            filters = {}
        
        # Non-admin users should only see active products
        if user_id:  # Simplified - assume logged in users see all
            pass
        else:
            filters['status'] = 'active'
        
        return filters

    async def _post_create_actions(
        self,
        product: Product,
        user_id: Optional[UUID]
    ) -> None:
        """Post-creation business logic."""
        # This could include:
        # - Sending notifications
        # - Updating search indexes
        # - Creating audit logs
        pass

    async def _post_update_actions(
        self,
        old_product: Product,
        new_product: Product,
        user_id: Optional[UUID]
    ) -> None:
        """Post-update business logic."""
        # This could include:
        # - Invalidating caches
        # - Updating search indexes
        # - Sending notifications for significant changes
        pass