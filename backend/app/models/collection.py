from datetime import date
from typing import List, TYPE_CHECKING

from sqlalchemy import Column, String, Integer, Text, Date, JSON, Index
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.file import File


class Collection(BaseModel):
    """
    Fashion Collection Model
    
    Represents a seasonal fashion collection with products,
    technical files, and marketing materials.
    """
    __tablename__ = "collections"
    
    # Basic Information
    name = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Collection name (e.g., 'Summer Breeze 2024')"
    )
    
    slug = Column(
        String(120),
        unique=True,
        nullable=False,
        index=True,
        doc="URL-friendly slug for the collection"
    )
    
    season = Column(
        String(20),
        nullable=False,
        index=True,
        doc="Season (Spring, Summer, Fall, Winter)"
    )
    
    year = Column(
        Integer,
        nullable=False,
        index=True,
        doc="Collection year"
    )
    
    # Description and Marketing
    description = Column(
        Text,
        nullable=True,
        doc="Detailed collection description"
    )
    
    short_description = Column(
        String(500),
        nullable=True,
        doc="Brief collection summary for previews"
    )
    
    # Business Information
    order_start_date = Column(
        Date,
        nullable=True,
        doc="Order period start date"
    )
    
    order_end_date = Column(
        Date,
        nullable=True,
        doc="Order period end date"
    )
    
    # Status and Visibility
    status = Column(
        String(20),
        default="draft",
        nullable=False,
        index=True,
        doc="Collection status (draft, active, archived)"
    )
    
    is_published = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Whether collection is publicly visible"
    )
    
    # Metadata and Settings
    metadata = Column(
        JSON,
        default=dict,
        nullable=True,
        doc="Additional collection metadata and settings"
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
    
    # Relationships
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="collection",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    files: Mapped[List["File"]] = relationship(
        "File",
        back_populates="collection",
        cascade="all, delete-orphan"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_collection_season_year", "season", "year"),
        Index("idx_collection_status_published", "status", "is_published"),
        Index("idx_collection_order_dates", "order_start_date", "order_end_date"),
    )
    
    def __repr__(self) -> str:
        return f"<Collection(name='{self.name}', season='{self.season}', year={self.year})>"
    
    @property
    def full_name(self) -> str:
        """Get full collection name with season and year."""
        return f"{self.name} - {self.season} {self.year}"
    
    @property
    def is_order_period_active(self) -> bool:
        """Check if the collection is currently in its order period."""
        if not self.order_start_date or not self.order_end_date:
            return False
        
        today = date.today()
        return self.order_start_date <= today <= self.order_end_date
    
    @property
    def product_count(self) -> int:
        """Get the number of products in this collection."""
        return len(self.products) if self.products else 0