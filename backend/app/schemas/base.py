"""
Base Pydantic Schemas

Provides common base classes and patterns for request/response serialization.
Includes pagination, error handling, and base CRUD schemas.
"""

from datetime import datetime
from typing import Generic, TypeVar, List, Optional, Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.types import PositiveInt


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )


class BaseResponseSchema(BaseSchema):
    """Base response schema with audit fields."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None  # Firebase UID
    updated_by: Optional[str] = None  # Firebase UID
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    notes: Optional[str] = None


class BaseCreateSchema(BaseSchema):
    """Base schema for create operations."""
    
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes")


class BaseUpdateSchema(BaseSchema):
    """Base schema for update operations."""
    
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes")


# Generic types for pagination
T = TypeVar('T')


class PaginationParams(BaseSchema):
    """Standard pagination parameters."""
    
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(20, ge=1, le=100, description="Number of items to return")
    order_by: Optional[str] = Field(None, description="Field to order by (prefix with '-' for desc)")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response."""
    
    items: List[T]
    total: int = Field(description="Total number of items")
    skip: int = Field(description="Number of items skipped")
    limit: int = Field(description="Number of items returned")
    has_next: bool = Field(description="Whether there are more items")
    has_prev: bool = Field(description="Whether there are previous items")
    page: int = Field(description="Current page number (1-based)")
    total_pages: int = Field(description="Total number of pages")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        skip: int,
        limit: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response from items and parameters."""
        page = (skip // limit) + 1
        total_pages = (total + limit - 1) // limit
        
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=skip + limit < total,
            has_prev=skip > 0,
            page=page,
            total_pages=total_pages
        )


class SearchParams(BaseSchema):
    """Standard search parameters."""
    
    query: Optional[str] = Field(None, description="Search query")
    category: Optional[str] = Field(None, description="Category filter")
    status: Optional[str] = Field(None, description="Status filter")
    

class FileResponse(BaseResponseSchema):
    """File upload response schema."""
    
    filename: str
    original_filename: str
    content_type: str
    size: int
    url: str
    metadata: Optional[Dict[str, Any]] = None


class BulkOperationResponse(BaseSchema):
    """Response for bulk operations."""
    
    success_count: int
    error_count: int
    total_count: int
    errors: Optional[List[Dict[str, Any]]] = None


class ErrorDetail(BaseSchema):
    """Error detail schema."""
    
    message: str
    code: Optional[str] = None
    field: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseSchema):
    """Standard error response schema."""
    
    detail: str
    error_code: Optional[str] = None
    errors: Optional[List[ErrorDetail]] = None
    context: Optional[Dict[str, Any]] = None


# Slug validation
def validate_slug(v: str) -> str:
    """Validate URL-friendly slug format."""
    if not v:
        raise ValueError("Slug cannot be empty")
    
    import re
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
        raise ValueError(
            "Slug must contain only lowercase letters, numbers, and hyphens. "
            "Cannot start or end with hyphen."
        )
    
    if len(v) < 3:
        raise ValueError("Slug must be at least 3 characters long")
    
    if len(v) > 100:
        raise ValueError("Slug must be no more than 100 characters long")
    
    return v


# URL validation
def validate_url(v: Optional[str]) -> Optional[str]:
    """Validate URL format."""
    if not v:
        return v
    
    from urllib.parse import urlparse
    try:
        result = urlparse(v)
        if not all([result.scheme, result.netloc]):
            raise ValueError("Invalid URL format")
        return v
    except Exception:
        raise ValueError("Invalid URL format")


# Currency validation
def validate_currency(v: str) -> str:
    """Validate ISO 4217 currency code."""
    valid_currencies = {"USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "SEK", "NOK", "DKK"}
    if v.upper() not in valid_currencies:
        raise ValueError(f"Currency must be one of: {', '.join(valid_currencies)}")
    return v.upper()


class StatusEnum:
    """Common status enums."""
    
    COLLECTION_STATUS = ["draft", "active", "archived"]
    PRODUCT_STATUS = ["active", "discontinued", "coming_soon"]
    SEASON = ["Spring", "Summer", "Fall", "Winter"]
    PRODUCT_CATEGORY = ["bikini", "one-piece", "accessory", "cover-up"]


# Common field definitions
def get_name_field(max_length: int = 100) -> Field:
    """Get a name field with validation."""
    return Field(
        ...,
        min_length=1,
        max_length=max_length,
        description="Name",
        examples=["Summer Breeze Collection", "Ocean Wave Bikini"]
    )


def get_slug_field() -> Field:
    """Get a slug field with validation."""
    return Field(
        ...,
        description="URL-friendly slug",
        examples=["summer-breeze-2024", "ocean-wave-bikini"]
    )


def get_description_field(required: bool = False) -> Field:
    """Get a description field."""
    return Field(
        None if not required else ...,
        max_length=2000,
        description="Detailed description"
    )


def get_short_description_field() -> Field:
    """Get a short description field."""
    return Field(
        None,
        max_length=500,
        description="Brief summary for previews"
    )


def get_price_field() -> Field:
    """Get a price field with validation."""
    return Field(
        None,
        ge=0,
        decimal_places=2,
        description="Price in specified currency"
    )
