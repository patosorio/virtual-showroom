"""
Enhanced Product Database Model

Updated to support all frontend component requirements with proper relationships.
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
    from app.models.product.variant import ProductVariant
    from app.models.product.image import ProductImage
    from app.models.product.technical_specification import TechnicalSpecification
    from app.models.product.technical_drawing import TechnicalDrawing
    from app.models.product.size_chart import SizeChart
    from app.models.file import File


class Product(BaseModel):
    """
    Enhanced Product Model
    
    Represents a swimwear product with complete support for:
    - Multiple variants with images
    - Technical specifications and drawings
    - Size charts and measurements
    - Product characteristics and features
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
        doc="Brief product summary for previews"
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
    
    # Product Characteristics (NEW - for VirtualShowroom component)
    material_composition = Column(
        Text,
        nullable=True,
        doc="Material composition (e.g., '78% Recycled PA, 22% EA')"
    )
    
    sustainability_features = Column(
        JSON,
        default=list,
        nullable=True,
        doc="Sustainability features list"
    )
    
    care_instructions = Column(
        JSON,
        default=list,
        nullable=True,
        doc="Care instructions list"
    )
    
    features = Column(
        JSON,
        default=list,
        nullable=True,
        doc="Product features list for display"
    )
    
    fit_notes = Column(
        Text,
        nullable=True,
        doc="Fit information (e.g., 'True to size fit', 'Model is 5\\'8\" wearing size S')"
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
    
    # Additional Metadata
    extra_data = Column(
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
    
    images: Mapped[List["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.sort_order"
    )
    
    specifications: Mapped[List["TechnicalSpecification"]] = relationship(
        "TechnicalSpecification",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="TechnicalSpecification.sort_order"
    )
    
    technical_drawings: Mapped[List["TechnicalDrawing"]] = relationship(
        "TechnicalDrawing",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="TechnicalDrawing.sort_order"
    )
    
    size_chart: Mapped["SizeChart"] = relationship(
        "SizeChart",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan"
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
    
    @property
    def main_image(self) -> "ProductImage":
        """Get the main product image."""
        if self.images:
            main_images = [img for img in self.images if img.type == "main"]
            if main_images:
                return main_images[0]
            return self.images[0]  # Fallback to first image
        return None
    
    @property
    def primary_variant(self) -> "ProductVariant":
        """Get the primary/first variant."""
        return self.variants[0] if self.variants else None
    
    @property
    def available_colors(self) -> List[str]:
        """Get list of available colors from variants."""
        if self.variants:
            return [variant.color for variant in self.variants]
        return []
    
    @property
    def price_range(self) -> dict:
        """Get price range considering variant adjustments."""
        base_price = self.retail_price or Decimal('0')
        
        if not self.variants:
            return {
                "min": base_price,
                "max": base_price,
                "currency": self.currency
            }
        
        prices = []
        for variant in self.variants:
            variant_price = base_price + (variant.price_adjustment or Decimal('0'))
            prices.append(variant_price)
        
        return {
            "min": min(prices),
            "max": max(prices),
            "currency": self.currency
        }
    
    def get_features_list(self) -> List[str]:
        """Get features as list of strings."""
        if isinstance(self.features, list):
            return self.features
        return []
    
    def get_care_instructions_list(self) -> List[str]:
        """Get care instructions as list of strings."""
        if isinstance(self.care_instructions, list):
            return self.care_instructions
        return []
    
    def get_sustainability_features_list(self) -> List[str]:
        """Get sustainability features as list of strings."""
        if isinstance(self.sustainability_features, list):
            return self.sustainability_features
        return []
