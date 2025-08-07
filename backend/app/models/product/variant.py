"""
Enhanced Product Variant Database Model

Updated to support variant-specific images and better size management.
"""

from decimal import Decimal
from typing import List, TYPE_CHECKING

from sqlalchemy import (
    Column, String, JSON, ForeignKey, 
    DECIMAL, Boolean, Integer, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product.product import Product
    from app.models.product.image import ProductImage


class ProductVariant(BaseModel):
    """
    Enhanced Product Variant Model
    
    Represents different color/style variations of a product
    with variant-specific images and size information.
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
        doc="Hex color code (e.g., '#0066CC')"
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
    
    # Size Information (Enhanced)
    available_sizes = Column(
        JSON,
        default=list,
        nullable=True,
        doc="Available sizes for this variant ['XS', 'S', 'M', 'L', 'XL']"
    )
    
    # Pricing (if different from product)
    price_adjustment = Column(
        DECIMAL(10, 2),
        default=0.00,
        nullable=True,
        doc="Price adjustment from base product price"
    )
    
    # Display Order
    sort_order = Column(
        Integer,
        default=0,
        doc="Display order for variants"
    )
    
    # Metadata
    extra_data = Column(
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
    
    images: Mapped[List["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="variant",
        cascade="all, delete-orphan",
        order_by="ProductImage.sort_order"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_variant_product_color", "product_id", "color"),
        Index("idx_variant_available", "is_available"),
        Index("idx_variant_sort", "product_id", "sort_order"),
    )
    
    def __repr__(self) -> str:
        product_name = self.product.name if self.product else 'Unknown'
        return f"<ProductVariant(product='{product_name}', color='{self.color}')>"
    
    @property
    def main_image(self) -> "ProductImage":
        """Get the main image for this variant."""
        if self.images:
            main_images = [img for img in self.images if img.type == "main"]
            if main_images:
                return main_images[0]
            return self.images[0]  # Fallback to first image
        return None
    
    @property
    def display_name(self) -> str:
        """Get display name for this variant."""
        if self.name and self.name != self.color:
            return f"{self.name} ({self.color})"
        return self.color
    
    def get_available_sizes_list(self) -> List[str]:
        """Get available sizes as list of strings."""
        if isinstance(self.available_sizes, list):
            return self.available_sizes
        return []
    
    def is_size_available(self, size: str) -> bool:
        """Check if a specific size is available for this variant."""
        available_sizes = self.get_available_sizes_list()
        return size in available_sizes
    
    def get_images_by_type(self, image_type: str) -> List["ProductImage"]:
        """Get images of a specific type for this variant."""
        if self.images:
            return [img for img in self.images if img.type == image_type]
        return []
    
    @property
    def final_price(self) -> Decimal:
        """Get final price including any adjustments."""
        base_price = self.product.retail_price or Decimal('0')
        adjustment = self.price_adjustment or Decimal('0')
        return base_price + adjustment