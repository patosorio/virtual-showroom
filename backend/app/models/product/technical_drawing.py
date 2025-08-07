"""
Technical Drawing Database Model

Handles technical drawings for products (front, back, side views).
Supports the TechnicalFilesViewer component requirements.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product.product import Product


class TechnicalDrawing(BaseModel):
    """
    Technical Drawing Model
    
    Stores technical drawings/schematics for products.
    Supports different views (front, back, side, detail).
    """
    __tablename__ = "technical_drawings"
    
    # Product Relationship
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to parent product"
    )
    
    # Drawing Information
    view = Column(
        String(20),
        nullable=False,
        index=True,
        doc="Drawing view: front, back, side, detail"
    )
    
    title = Column(
        String(100),
        nullable=True,
        doc="Display title for the drawing"
    )
    
    image_url = Column(
        String(500),
        nullable=False,
        doc="URL or path to the technical drawing image"
    )
    
    description = Column(
        Text,
        nullable=True,
        doc="Optional description of the technical drawing"
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
        doc="Image format (svg, png, jpg)"
    )
    
    # Display Information
    sort_order = Column(
        Integer,
        default=0,
        doc="Display order for technical drawings"
    )
    
    is_featured = Column(
        Boolean,
        default=False,
        doc="Whether this is a featured/primary technical drawing"
    )
    
    # Relationships
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="technical_drawings"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_tech_drawing_product_view", "product_id", "view"),
        Index("idx_tech_drawing_sort", "product_id", "sort_order"),
    )
    
    def __repr__(self) -> str:
        return f"<TechnicalDrawing(view='{self.view}', product_id='{self.product_id}')>"
    
    @property
    def display_title(self) -> str:
        """Get display title with fallback."""
        if self.title:
            return self.title
        return f"{self.view.title()} View"
    
    @property
    def aspect_ratio(self) -> float:
        """Calculate aspect ratio if dimensions are available."""
        if self.width and self.height:
            return self.width / self.height
        return 1.0
    
    @classmethod
    def create_standard_views(cls, product_id: str, base_url: str) -> list['TechnicalDrawing']:
        """Helper to create standard technical drawing views."""
        views = [
            {
                "view": "front",
                "title": "Front View - Technical Drawing",
                "sort_order": 1,
                "is_featured": True
            },
            {
                "view": "back", 
                "title": "Back View - Technical Drawing",
                "sort_order": 2
            },
            {
                "view": "side",
                "title": "Side View - Technical Drawing", 
                "sort_order": 3
            }
        ]
        
        drawings = []
        for view_data in views:
            drawing = cls(
                product_id=product_id,
                view=view_data["view"],
                title=view_data["title"],
                image_url=f"{base_url}/technical-drawings/{view_data['view']}.svg",
                sort_order=view_data["sort_order"],
                is_featured=view_data.get("is_featured", False)
            )
            drawings.append(drawing)
        
        return drawings