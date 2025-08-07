"""
Product Pydantic Schemas

Schemas for Product and related models (variants, images, specifications, etc.)
"""

from decimal import Decimal
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from .base import (
    BaseSchema, BaseResponseSchema, BaseCreateSchema, BaseUpdateSchema,
    validate_slug, get_name_field, get_description_field,
    get_short_description_field, get_price_field, validate_currency,
    StatusEnum
)


# Product Variant Schemas

class ProductVariantBase(BaseSchema):
    """Base schema for product variants."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Variant name")
    color: str = Field(..., min_length=1, max_length=50, description="Color name")
    color_code: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Hex color code")
    size: Optional[str] = Field(None, max_length=20, description="Size designation")
    sku_suffix: str = Field(..., min_length=1, max_length=20, description="SKU suffix for this variant")
    price_adjustment: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Price adjustment from base product price"
    )
    sort_order: int = Field(default=0, ge=0, description="Display order")
    is_available: bool = Field(default=True, description="Whether variant is available")
    stock_quantity: Optional[int] = Field(None, ge=0, description="Stock quantity")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional variant data")


class ProductVariantCreate(ProductVariantBase, BaseCreateSchema):
    """Schema for creating product variant."""
    pass


class ProductVariantUpdate(BaseUpdateSchema):
    """Schema for updating product variant."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Variant name")
    color: Optional[str] = Field(None, min_length=1, max_length=50, description="Color name")
    color_code: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Hex color code")
    size: Optional[str] = Field(None, max_length=20, description="Size designation")
    sku_suffix: Optional[str] = Field(None, min_length=1, max_length=20, description="SKU suffix")
    price_adjustment: Optional[Decimal] = Field(None, decimal_places=2, description="Price adjustment")
    sort_order: Optional[int] = Field(None, ge=0, description="Display order")
    is_available: Optional[bool] = Field(None, description="Whether variant is available")
    stock_quantity: Optional[int] = Field(None, ge=0, description="Stock quantity")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional variant data")


class ProductVariantResponse(ProductVariantBase, BaseResponseSchema):
    """Schema for product variant response."""
    
    product_id: UUID
    full_sku: str = Field(description="Complete SKU including product SKU and variant suffix")
    final_price: Decimal = Field(description="Final price including adjustments")
    images: Optional[List["ProductImageResponse"]] = None


# Product Image Schemas

class ProductImageBase(BaseSchema):
    """Base schema for product images."""
    
    filename: str = Field(..., description="Image filename")
    original_filename: str = Field(..., description="Original uploaded filename")
    url: str = Field(..., description="Image URL")
    alt_text: Optional[str] = Field(None, max_length=200, description="Alt text for accessibility")
    type: str = Field(
        default="gallery",
        description="Image type",
        examples=["main", "gallery", "detail", "back", "side"]
    )
    sort_order: int = Field(default=0, ge=0, description="Display order")
    width: Optional[int] = Field(None, gt=0, description="Image width in pixels")
    height: Optional[int] = Field(None, gt=0, description="Image height in pixels")
    file_size: Optional[int] = Field(None, gt=0, description="File size in bytes")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional image metadata")


class ProductImageCreate(ProductImageBase, BaseCreateSchema):
    """Schema for creating product image."""
    
    variant_id: Optional[UUID] = Field(None, description="Associated variant ID (if variant-specific)")


class ProductImageUpdate(BaseUpdateSchema):
    """Schema for updating product image."""
    
    alt_text: Optional[str] = Field(None, max_length=200, description="Alt text")
    type: Optional[str] = Field(None, description="Image type")
    sort_order: Optional[int] = Field(None, ge=0, description="Display order")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ProductImageResponse(ProductImageBase, BaseResponseSchema):
    """Schema for product image response."""
    
    product_id: UUID
    variant_id: Optional[UUID] = None


# Technical Specification Schemas

class TechnicalSpecificationBase(BaseSchema):
    """Base schema for technical specifications."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Specification name")
    value: str = Field(..., min_length=1, max_length=500, description="Specification value")
    unit: Optional[str] = Field(None, max_length=20, description="Unit of measurement")
    category: Optional[str] = Field(None, max_length=50, description="Specification category")
    sort_order: int = Field(default=0, ge=0, description="Display order")
    is_highlighted: bool = Field(default=False, description="Whether to highlight this spec")


class TechnicalSpecificationCreate(TechnicalSpecificationBase, BaseCreateSchema):
    """Schema for creating technical specification."""
    pass


class TechnicalSpecificationUpdate(BaseUpdateSchema):
    """Schema for updating technical specification."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Specification name")
    value: Optional[str] = Field(None, min_length=1, max_length=500, description="Specification value")
    unit: Optional[str] = Field(None, max_length=20, description="Unit of measurement")
    category: Optional[str] = Field(None, max_length=50, description="Specification category")
    sort_order: Optional[int] = Field(None, ge=0, description="Display order")
    is_highlighted: Optional[bool] = Field(None, description="Whether to highlight")


class TechnicalSpecificationResponse(TechnicalSpecificationBase, BaseResponseSchema):
    """Schema for technical specification response."""
    
    product_id: UUID


# Size Chart Schemas

class SizeChartEntryBase(BaseSchema):
    """Base schema for size chart entries."""
    
    size: str = Field(..., description="Size designation")
    measurements: Dict[str, Union[str, float]] = Field(
        ...,
        description="Measurements dictionary (e.g., {'bust': 34, 'waist': 26, 'hips': 36})"
    )


class SizeChartBase(BaseSchema):
    """Base schema for size charts."""
    
    name: Optional[str] = Field(None, max_length=100, description="Size chart name")
    description: Optional[str] = Field(None, max_length=500, description="Size chart description")
    measurement_unit: str = Field(default="inches", description="Measurement unit")
    entries: List[SizeChartEntryBase] = Field(..., description="Size chart entries")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class SizeChartCreate(SizeChartBase, BaseCreateSchema):
    """Schema for creating size chart."""
    pass


class SizeChartUpdate(BaseUpdateSchema):
    """Schema for updating size chart."""
    
    name: Optional[str] = Field(None, max_length=100, description="Size chart name")
    description: Optional[str] = Field(None, max_length=500, description="Size chart description")
    measurement_unit: Optional[str] = Field(None, description="Measurement unit")
    entries: Optional[List[SizeChartEntryBase]] = Field(None, description="Size chart entries")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SizeChartResponse(SizeChartBase, BaseResponseSchema):
    """Schema for size chart response."""
    
    product_id: UUID


# Main Product Schemas

class ProductBase(BaseSchema):
    """Base schema for products."""
    
    name: str = get_name_field(100)
    sku: str = Field(..., min_length=3, max_length=50, description="Stock Keeping Unit")
    category: str = Field(..., description="Product category")
    description: Optional[str] = get_description_field()
    short_description: Optional[str] = get_short_description_field()
    wholesale_price: Optional[Decimal] = get_price_field()
    retail_price: Optional[Decimal] = get_price_field()
    currency: str = Field(default="EUR", description="Currency code")
    material_composition: Optional[str] = Field(None, max_length=500, description="Material composition")
    sustainability_features: Optional[List[str]] = Field(
        default_factory=list,
        description="List of sustainability features"
    )
    care_instructions: Optional[List[str]] = Field(
        default_factory=list,
        description="List of care instructions"
    )
    features: Optional[List[str]] = Field(
        default_factory=list,
        description="List of product features"
    )
    fit_notes: Optional[str] = Field(None, max_length=500, description="Fit information")
    seo_title: Optional[str] = Field(None, max_length=200, description="SEO page title")
    seo_description: Optional[str] = Field(None, max_length=500, description="SEO meta description")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category value."""
        if v not in StatusEnum.PRODUCT_CATEGORY:
            raise ValueError(f"Category must be one of: {', '.join(StatusEnum.PRODUCT_CATEGORY)}")
        return v
    
    @field_validator('currency')
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        """Validate currency code."""
        return validate_currency(v)
    
    @field_validator('sku')
    @classmethod
    def validate_sku_format(cls, v: str) -> str:
        """Validate SKU format."""
        import re
        if not re.match(r'^[A-Z0-9\-_]+$', v.upper()):
            raise ValueError("SKU must contain only letters, numbers, hyphens, and underscores")
        return v.upper()


class ProductCreate(ProductBase, BaseCreateSchema):
    """Schema for creating a new product."""
    
    collection_id: UUID = Field(..., description="Collection ID this product belongs to")
    status: str = Field(default="active", description="Product status")
    is_featured: bool = Field(default=False, description="Whether product is featured")
    
    # Nested creation schemas
    variants: Optional[List[ProductVariantCreate]] = Field(
        default_factory=list,
        description="Product variants to create"
    )
    specifications: Optional[List[TechnicalSpecificationCreate]] = Field(
        default_factory=list,
        description="Technical specifications to create"
    )
    size_chart: Optional[SizeChartCreate] = Field(None, description="Size chart to create")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status value."""
        if v not in StatusEnum.PRODUCT_STATUS:
            raise ValueError(f"Status must be one of: {', '.join(StatusEnum.PRODUCT_STATUS)}")
        return v
    
    @model_validator(mode='after')
    def validate_product_data(self):
        """Validate product data consistency."""
        # Ensure at least one variant if variants are provided
        if self.variants and len(self.variants) == 0:
            raise ValueError("If variants are provided, at least one variant is required")
        
        # Validate price consistency
        if self.wholesale_price and self.retail_price:
            if self.wholesale_price >= self.retail_price:
                raise ValueError("Wholesale price must be less than retail price")
        
        return self


class ProductUpdate(BaseUpdateSchema):
    """Schema for updating an existing product."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Product name")
    sku: Optional[str] = Field(None, min_length=3, max_length=50, description="SKU")
    category: Optional[str] = Field(None, description="Product category")
    description: Optional[str] = Field(None, max_length=2000, description="Description")
    short_description: Optional[str] = Field(None, max_length=500, description="Short description")
    collection_id: Optional[UUID] = Field(None, description="Collection ID")
    wholesale_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Wholesale price")
    retail_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Retail price")
    currency: Optional[str] = Field(None, description="Currency code")
    material_composition: Optional[str] = Field(None, max_length=500, description="Material composition")
    sustainability_features: Optional[List[str]] = Field(None, description="Sustainability features")
    care_instructions: Optional[List[str]] = Field(None, description="Care instructions")
    features: Optional[List[str]] = Field(None, description="Product features")
    fit_notes: Optional[str] = Field(None, max_length=500, description="Fit information")
    status: Optional[str] = Field(None, description="Product status")
    is_featured: Optional[bool] = Field(None, description="Whether product is featured")
    seo_title: Optional[str] = Field(None, max_length=200, description="SEO title")
    seo_description: Optional[str] = Field(None, max_length=500, description="SEO description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        """Validate category value."""
        if v and v not in StatusEnum.PRODUCT_CATEGORY:
            raise ValueError(f"Category must be one of: {', '.join(StatusEnum.PRODUCT_CATEGORY)}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status value."""
        if v and v not in StatusEnum.PRODUCT_STATUS:
            raise ValueError(f"Status must be one of: {', '.join(StatusEnum.PRODUCT_STATUS)}")
        return v
    
    @field_validator('currency')
    @classmethod
    def validate_currency_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate currency code."""
        return validate_currency(v) if v else v
    
    @field_validator('sku')
    @classmethod
    def validate_sku_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate SKU format."""
        if not v:
            return v
        import re
        if not re.match(r'^[A-Z0-9\-_]+$', v.upper()):
            raise ValueError("SKU must contain only letters, numbers, hyphens, and underscores")
        return v.upper()


class ProductResponse(ProductBase, BaseResponseSchema):
    """Schema for product response with all relationships."""
    
    collection_id: UUID
    status: str
    is_featured: bool
    
    # Computed fields
    variant_count: int = Field(description="Number of variants")
    available_colors: List[str] = Field(description="Available color options")
    price_range: Dict[str, Union[str, Decimal]] = Field(description="Price range with currency")
    
    # Nested relationships (optional based on load_relations)
    collection: Optional["CollectionSummary"] = None
    variants: Optional[List[ProductVariantResponse]] = None
    images: Optional[List[ProductImageResponse]] = None
    specifications: Optional[List[TechnicalSpecificationResponse]] = None
    size_chart: Optional[SizeChartResponse] = None
    
    @field_validator('available_colors', mode='before')
    @classmethod
    def ensure_colors_list(cls, v):
        """Ensure available_colors is a list."""
        if isinstance(v, str):
            return [v]
        return v or []


class ProductSummaryResponse(BaseSchema):
    """Summary schema for product references."""
    
    id: UUID
    name: str
    sku: str
    category: str
    status: str
    is_featured: bool
    retail_price: Optional[Decimal]
    currency: str
    variant_count: int
    main_image_url: Optional[str] = Field(None, description="URL of main product image")


class ProductListFilters(BaseSchema):
    """Filters for product listing."""
    
    collection_id: Optional[UUID] = Field(None, description="Filter by collection")
    category: Optional[str] = Field(None, description="Filter by category")
    status: Optional[str] = Field(None, description="Filter by status")
    is_featured: Optional[bool] = Field(None, description="Filter by featured status")
    color: Optional[str] = Field(None, description="Filter by available color")
    price_min: Optional[Decimal] = Field(None, ge=0, description="Minimum price filter")
    price_max: Optional[Decimal] = Field(None, ge=0, description="Maximum price filter")
    query: Optional[str] = Field(None, description="Search query for name/description/SKU")
    has_variants: Optional[bool] = Field(None, description="Filter products with/without variants")
    has_images: Optional[bool] = Field(None, description="Filter products with/without images")


class ProductSearchResult(BaseSchema):
    """Product search result with relevance."""
    
    product: ProductSummaryResponse
    relevance_score: float = Field(description="Search relevance score")
    match_fields: List[str] = Field(description="Fields that matched the search")


class ProductAnalytics(BaseSchema):
    """Product analytics data."""
    
    total_variants: int
    total_images: int
    variants_by_color: Dict[str, int]
    average_price: Optional[Decimal]
    specifications_count: int
    has_size_chart: bool


# File Upload Schemas

class ProductImageUploadRequest(BaseSchema):
    """Request schema for product image upload."""
    
    variant_id: Optional[UUID] = Field(None, description="Associate with specific variant")
    type: str = Field(default="gallery", description="Image type")
    alt_text: Optional[str] = Field(None, max_length=200, description="Alt text")
    sort_order: Optional[int] = Field(None, ge=0, description="Display order")


class BulkProductImportItem(BaseSchema):
    """Schema for bulk product import item."""
    
    name: str
    sku: str
    category: str
    collection_slug: str
    description: Optional[str] = None
    retail_price: Optional[Decimal] = None
    wholesale_price: Optional[Decimal] = None
    currency: str = "EUR"
    variants: Optional[List[Dict[str, Any]]] = None


class BulkProductImportRequest(BaseSchema):
    """Request schema for bulk product import."""
    
    products: List[BulkProductImportItem]
    update_existing: bool = Field(default=False, description="Whether to update existing products")
    collection_id: Optional[UUID] = Field(None, description="Default collection for products without collection_slug")


# Forward references
from .collection import CollectionSummary

ProductResponse.model_rebuild()
ProductVariantResponse.model_rebuild()
