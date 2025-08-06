"""
Product Database Models

Defines the database schema for products, variants, and specifications
in the Virtual Showroom application.
"""

from decimal import Decimal
from typing import List, TYPE_CHECKING

from sqlalchemy import (
    Column, String, Text, JSON, ForeignKey, 
    DECIMAL, Boolean, Integer, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.collection import Collection
    from app.models.file import File


class Product(BaseModel):
    """
    Product Model
    
    Represents a swimwear product with variants, specifications,
    and pricing information.
    """
    __tablename__ = "products"
    
    # Basic Information
    name = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Product name"
    )
    
    sku = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Stock Keeping Unit identifier"
    )
    
    category = Column(
        String(50),
        nullable=False,
        index=True,
        doc="Product category (bikini, one-piece, accessory)"
    )
    
    # Description and Details
    description = Column(
        Text,
        nullable=True,
        doc="Detailed product description"
    )
    
    short_description = Column(
        String(500),
        nullable=True,
        doc="Brief product summary"
    )
    
    # Collection Relationship
    collection_id = Column(
        UUID(as_uuid=True),
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to parent collection"
    )
    
    # Pricing Information
    wholesale_price = Column(
        DECIMAL(10, 2),
        nullable=True,
        doc="Wholesale price"
    )
    
    retail_price = Column(
        DECIMAL(10, 2),
        nullable=True,
        doc="Suggested retail price"
    )
    
    currency = Column(
        String(3),
        default="EUR",
        nullable=False,
        doc="Price currency code (ISO 4217)"
    )
    
    # Product Status
    status = Column(
        String(20),
        default="active",
        nullable=False,
        index=True,
        doc="Product status (active, discontinued, coming_soon)"
    )
    
    is_featured = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Whether product is featured"
    )
    
    # Technical Information
    specifications = Column(
        JSON,
        default=dict,
        nullable=True,
        doc="Technical specifications and materials"
    )
    
    # SEO and Marketing
    seo_title = Column(
        String(200),
        nullable=True,
        doc="SEO page title"
    )
    
    seo_description = Column(
        String(500),
        nullable=True,
        doc="SEO meta description"
    )
    
    # Metadata
    metadata = Column(
        JSON,
        default=dict,
        nullable=True,
        doc="Additional product metadata"
    )
    
    # Relationships
    collection: Mapped["Collection"] = relationship(
        "Collection",
        back_populates="products"
    )
    
    variants: Mapped[List["ProductVariant"]] = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    files: Mapped[List["File"]] = relationship(
        "File",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_product_collection_status", "collection_id", "status"),
        Index("idx_product_category_featured", "category", "is_featured"),
    )
    
    def __repr__(self) -> str:
        return f"<Product(name='{self.name}', sku='{self.sku}')>"
    
    @property
    def variant_count(self) -> int:
        """Get the number of variants for this product."""
        return len(self.variants) if self.variants else 0


class ProductVariant(BaseModel):
    """
    Product Variant Model
    
    Represents different color/style variations of a product
    with size and availability information.
    """
    __tablename__ = "product_variants"
    
    # Product Relationship
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to parent product"
    )
    
    # Variant Information
    name = Column(
        String(100),
        nullable=False,
        doc="Variant name (e.g., 'Ocean Blue')"
    )
    
    color = Column(
        String(50),
        nullable=False,
        index=True,
        doc="Color name"
    )
    
    color_code = Column(
        String(7),
        nullable=True,
        doc="Hex color code (e.g., '#FF5733')"
    )
    
    # Variant SKU
    sku = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Variant-specific SKU"
    )
    
    # Availability and Inventory
    is_available = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="Whether variant is available"
    )
    
    # Size and Fit Information
    sizes_available = Column(
        JSON,
        default=list,
        nullable=True,
        doc="Available sizes with measurements"
    )
    
    # Pricing (if different from product)
    price_adjustment = Column(
        DECIMAL(10, 2),
        default=0.00,
        nullable=True,
        doc="Price adjustment from base product price"
    )
    
    # Metadata
    metadata = Column(
        JSON,
        default=dict,
        nullable=True,
        doc="Additional variant metadata"
    )
    
    # Relationships
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="variants"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_variant_product_color", "product_id", "color"),
        Index("idx_variant_available", "is_available"),
    )
    
    def __repr__(self) -> str:
        return f"<ProductVariant(product='{self.product.name if self.product else 'N/A'}', color='{self.color}')>"