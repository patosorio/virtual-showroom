"""
Size Chart Database Model

Handles size charts for products with international sizing.
Supports the TechnicalFilesViewer component size chart requirements.
"""

from typing import TYPE_CHECKING, List, Dict, Any

from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product.product import Product


class SizeChart(BaseModel):
    """
    Size Chart Model
    
    Stores size chart information for products.
    Supports international sizing with customizable measurements.
    """
    __tablename__ = "size_charts"
    
    # Product Relationship (one-to-one)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        doc="Reference to parent product (one-to-one)"
    )
    
    # Chart Information
    name = Column(
        String(100),
        nullable=True,
        doc="Chart name (e.g., 'International Sizing')"
    )
    
    chart_type = Column(
        String(20),
        default="standard",
        doc="Chart type: standard, plus_size, kids, maternity"
    )
    
    # Size Data (JSON structure)
    sizes = Column(
        JSON,
        nullable=False,
        doc="Array of size objects with measurements"
    )
    # Example structure:
    # [
    #   {
    #     "size": "XS",
    #     "uk": "6", 
    #     "eu": "34",
    #     "us": "2",
    #     "bust": "32",
    #     "waist": "24",
    #     "hip": "34"
    #   }
    # ]
    
    # Additional Information
    measurement_unit = Column(
        String(10),
        default="inches",
        doc="Measurement unit: inches, cm"
    )
    
    notes = Column(
        Text,
        nullable=True,
        doc="Fit notes, measurement instructions"
    )
    
    # Relationships
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="size_chart"
    )
    
    def __repr__(self) -> str:
        return f"<SizeChart(product_id='{self.product_id}', type='{self.chart_type}')>"
    
    def get_sizes_list(self) -> List[Dict[str, Any]]:
        """Get sizes as list of dictionaries."""
        if isinstance(self.sizes, list):
            return self.sizes
        return []
    
    def get_available_sizes(self) -> List[str]:
        """Get list of available size names."""
        sizes = self.get_sizes_list()
        return [size.get("size", "") for size in sizes if size.get("size")]
    
    def get_size_by_name(self, size_name: str) -> Dict[str, Any]:
        """Get specific size measurements by size name."""
        sizes = self.get_sizes_list()
        for size in sizes:
            if size.get("size") == size_name:
                return size
        return {}
    
    @classmethod
    def create_standard_chart(cls, product_id: str) -> 'SizeChart':
        """Helper to create standard international size chart."""
        standard_sizes = [
            {"size": "XS", "uk": "6", "eu": "34", "us": "2", "bust": "32", "waist": "24", "hip": "34"},
            {"size": "S", "uk": "8", "eu": "36", "us": "4", "bust": "34", "waist": "26", "hip": "36"},
            {"size": "M", "uk": "10", "eu": "38", "us": "6", "bust": "36", "waist": "28", "hip": "38"},
            {"size": "L", "uk": "12", "eu": "40", "us": "8", "bust": "38", "waist": "30", "hip": "40"},
            {"size": "XL", "uk": "14", "eu": "42", "us": "10", "bust": "40", "waist": "32", "hip": "42"}
        ]
        
        return cls(
            product_id=product_id,
            name="International Sizing",
            chart_type="standard",
            sizes=standard_sizes,
            measurement_unit="inches",
            notes="All measurements are in inches. Model is 5'8\" wearing size S."
        )