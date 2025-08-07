"""
Technical Specification Database Model

Handles structured technical specifications for products.
Supports the SpecificationPanel component requirements.
"""

from typing import TYPE_CHECKING, Dict, Any

from sqlalchemy import Column, String, JSON, Integer, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product.product import Product


class TechnicalSpecification(BaseModel):
    """
    Technical Specification Model
    
    Stores structured technical specifications for products.
    Supports expandable sections in the frontend.
    """
    __tablename__ = "technical_specifications"
    
    # Product Relationship
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to parent product"
    )
    
    # Specification Information
    type = Column(
        String(30),
        nullable=False,
        index=True,
        doc="Specification type (material, construction, care, sizing, sustainability)"
    )
    
    title = Column(
        String(100),
        nullable=False,
        doc="Display title for the specification section"
    )
    
    content = Column(
        JSON,
        nullable=False,
        doc="Structured specification content"
    )
    
    sort_order = Column(
        Integer,
        default=0,
        doc="Display order in specification list"
    )
    
    is_expandable = Column(
        Boolean,
        default=True,
        doc="Whether this specification can be expanded/collapsed"
    )
    
    is_expanded_by_default = Column(
        Boolean,
        default=False,
        doc="Whether this specification should be expanded by default"
    )
    
    # Relationships
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="specifications"
    )
    
    # Index for performance
    __table_args__ = (
        Index("idx_tech_spec_product_type", "product_id", "type"),
        Index("idx_tech_spec_sort", "product_id", "sort_order"),
    )
    
    def __repr__(self) -> str:
        return f"<TechnicalSpecification(type='{self.type}', product_id='{self.product_id}')>"
    
    def get_content_as_dict(self) -> Dict[str, Any]:
        """Get content as dictionary for API responses."""
        if isinstance(self.content, dict):
            return self.content
        return {}
    
    @classmethod
    def create_material_spec(cls, product_id: str, material_data: Dict[str, Any]) -> 'TechnicalSpecification':
        """Helper to create material specification."""
        return cls(
            product_id=product_id,
            type="material",
            title="Materials & Construction",
            content={
                "composition": material_data.get("composition"),
                "material_name": material_data.get("material_name"),
                "certifications": material_data.get("certifications", []),
                "sustainability": material_data.get("sustainability", [])
            },
            sort_order=1,
            is_expanded_by_default=True
        )
    
    @classmethod
    def create_construction_spec(cls, product_id: str, construction_data: Dict[str, Any]) -> 'TechnicalSpecification':
        """Helper to create construction specification."""
        return cls(
            product_id=product_id,
            type="construction",
            title="Technical Details",
            content=construction_data,
            sort_order=2
        )
    
    @classmethod
    def create_care_spec(cls, product_id: str, care_instructions: list) -> 'TechnicalSpecification':
        """Helper to create care instructions specification."""
        return cls(
            product_id=product_id,
            type="care",
            title="Care Instructions",
            content={
                "instructions": care_instructions
            },
            sort_order=3
        )