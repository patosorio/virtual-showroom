"""
Product Image Database Model

Handles product images for different variants and display types.
Supports the frontend image display requirements.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product.product import Product
    from app.models.product.variant import ProductVariant


class ProductImage(BaseModel):
    """
    Product Image Model
    
    Stores images for products and their variants.
    Supports different image types (main, detail, lifestyle, thumbnail).
    """
    __tablename__ = "product_images"
    
    # Relationships
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to parent product"
    )
    
    variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        doc="Reference to specific variant (optional)"
    )
    
    # Image Information
    url = Column(
        String(500),
        nullable=False,
        doc="Image URL or path"
    )
    
    alt = Column(
        String(200),
        nullable=True,
        doc="Alt text for accessibility"
    )
    
    type = Column(
        String(20),
        nullable=False,
        index=True,
        doc="Image type: main, detail, lifestyle, thumbnail"
    )
    
    sort_order = Column(
        Integer,
        default=0,
        doc="Display order for image gallery"
    )
    
    # File Metadata
    file_size = Column(
        Integer,
        nullable=True,
        doc="File size in bytes"
    )
    
    width = Column(
        Integer,
        nullable=True,
        doc="Image width in pixels"
    )
    
    height = Column(
        Integer,
        nullable=True,
        doc="Image height in pixels"
    )
    
    format = Column(
        String(10),
        nullable=True,
        doc="Image format (jpg, png, webp)"
    )
    
    # Relationships
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="images"
    )
    
    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant",
        back_populates="images"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_product_image_type_order", "product_id", "type", "sort_order"),
        Index("idx_variant_image_type_order", "variant_id", "type", "sort_order"),
    )
    
    def __repr__(self) -> str:
        return f"<ProductImage(type='{self.type}', product_id='{self.product_id}')>"
    
    @property
    def is_main_image(self) -> bool:
        """Check if this is a main product image."""
        return self.type == "main"
    
    @property
    def aspect_ratio(self) -> float:
        """Calculate aspect ratio if dimensions are available."""
        if self.width and self.height:
            return self.width / self.height
        return 1.0