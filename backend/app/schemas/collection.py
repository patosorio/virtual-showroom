"""
Collection Pydantic Schemas

Schemas for Collection CRUD operations, validation, and serialization.
"""

from datetime import date
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import Field, field_validator

from .base import (
    BaseSchema, BaseResponseSchema, BaseCreateSchema, BaseUpdateSchema,
    validate_slug, get_name_field, get_slug_field, get_description_field,
    get_short_description_field, StatusEnum
)


# Collection Schemas

class CollectionBase(BaseSchema):
    """Base collection schema with common fields."""
    
    name: str = get_name_field(100)
    slug: str = get_slug_field()
    season: str = Field(
        ...,
        description="Season",
        examples=["Spring", "Summer", "Fall", "Winter"]
    )
    year: int = Field(
        ...,
        ge=2020,
        le=2030,
        description="Collection year",
        examples=[2024, 2025]
    )
    description: Optional[str] = get_description_field()
    short_description: Optional[str] = get_short_description_field()
    order_start_date: Optional[date] = Field(
        None,
        description="Order period start date"
    )
    order_end_date: Optional[date] = Field(
        None,
        description="Order period end date"
    )
    seo_title: Optional[str] = Field(
        None,
        max_length=200,
        description="SEO page title"
    )
    seo_description: Optional[str] = Field(
        None,
        max_length=500,
        description="SEO meta description"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional collection metadata"
    )
    
    @field_validator('slug')
    @classmethod
    def validate_slug_format(cls, v: str) -> str:
        """Validate slug format."""
        return validate_slug(v)
    
    @field_validator('season')
    @classmethod
    def validate_season(cls, v: str) -> str:
        """Validate season value."""
        if v not in StatusEnum.SEASON:
            raise ValueError(f"Season must be one of: {', '.join(StatusEnum.SEASON)}")
        return v
    
    @field_validator('order_end_date')
    @classmethod
    def validate_order_dates(cls, v: Optional[date], info) -> Optional[date]:
        """Validate that end date is after start date."""
        if v and 'order_start_date' in info.data:
            start_date = info.data['order_start_date']
            if start_date and v <= start_date:
                raise ValueError("Order end date must be after start date")
        return v


class CollectionCreate(CollectionBase, BaseCreateSchema):
    """Schema for creating a new collection."""
    
    status: str = Field(
        default="draft",
        description="Collection status",
        examples=["draft", "active", "archived"]
    )
    is_published: bool = Field(
        default=False,
        description="Whether collection is publicly visible"
    )
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status value."""
        if v not in StatusEnum.COLLECTION_STATUS:
            raise ValueError(f"Status must be one of: {', '.join(StatusEnum.COLLECTION_STATUS)}")
        return v


class CollectionUpdate(BaseUpdateSchema):
    """Schema for updating an existing collection."""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Collection name"
    )
    slug: Optional[str] = Field(
        None,
        description="URL-friendly slug"
    )
    season: Optional[str] = Field(
        None,
        description="Season"
    )
    year: Optional[int] = Field(
        None,
        ge=2020,
        le=2030,
        description="Collection year"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Detailed description"
    )
    short_description: Optional[str] = Field(
        None,
        max_length=500,
        description="Brief summary"
    )
    order_start_date: Optional[date] = Field(
        None,
        description="Order period start date"
    )
    order_end_date: Optional[date] = Field(
        None,
        description="Order period end date"
    )
    status: Optional[str] = Field(
        None,
        description="Collection status"
    )
    is_published: Optional[bool] = Field(
        None,
        description="Whether collection is publicly visible"
    )
    seo_title: Optional[str] = Field(
        None,
        max_length=200,
        description="SEO page title"
    )
    seo_description: Optional[str] = Field(
        None,
        max_length=500,
        description="SEO meta description"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata"
    )
    
    @field_validator('slug')
    @classmethod
    def validate_slug_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate slug format."""
        return validate_slug(v) if v else v
    
    @field_validator('season')
    @classmethod
    def validate_season(cls, v: Optional[str]) -> Optional[str]:
        """Validate season value."""
        if v and v not in StatusEnum.SEASON:
            raise ValueError(f"Season must be one of: {', '.join(StatusEnum.SEASON)}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status value."""
        if v and v not in StatusEnum.COLLECTION_STATUS:
            raise ValueError(f"Status must be one of: {', '.join(StatusEnum.COLLECTION_STATUS)}")
        return v


class CollectionResponse(CollectionBase, BaseResponseSchema):
    """Schema for collection response with relationships."""
    
    status: str
    is_published: bool
    product_count: int = Field(description="Number of products in collection")
    is_order_period_active: bool = Field(description="Whether order period is currently active")
    full_name: str = Field(description="Full collection name with season and year")
    
    # Optional nested relationships
    products: Optional[List["ProductSummaryResponse"]] = None
    files: Optional[List["FileResponse"]] = None


class CollectionSummary(BaseSchema):
    """Summary schema for collection references."""
    
    id: UUID
    name: str
    slug: str
    season: str
    year: int
    status: str
    is_published: bool
    product_count: int
    full_name: str


class CollectionListFilters(BaseSchema):
    """Filters for collection listing."""
    
    season: Optional[str] = Field(None, description="Filter by season")
    year: Optional[int] = Field(None, description="Filter by year")
    status: Optional[str] = Field(None, description="Filter by status")
    is_published: Optional[bool] = Field(None, description="Filter by published status")
    query: Optional[str] = Field(None, description="Search query for name/description")
    has_products: Optional[bool] = Field(None, description="Filter collections with/without products")


class CollectionPublishRequest(BaseSchema):
    """Request schema for publishing a collection."""
    
    publish: bool = Field(description="Whether to publish or unpublish")
    seo_title: Optional[str] = Field(None, max_length=200, description="SEO title")
    seo_description: Optional[str] = Field(None, max_length=500, description="SEO description")


class CollectionAnalytics(BaseSchema):
    """Collection analytics data."""
    
    total_products: int
    products_by_category: Dict[str, int]
    products_by_status: Dict[str, int]
    average_price: Optional[float]
    price_range: Dict[str, float]
    last_updated: Optional[date]


# Forward references for type hints
from .product import ProductSummaryResponse
from .file import FileResponse

CollectionResponse.model_rebuild()
