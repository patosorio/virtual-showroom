"""
File Database Model

Represents uploaded files and their metadata.
"""

from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.collection import Collection
    from app.models.product.product import Product


class File(BaseModel):
    """
    File Model
    
    Represents uploaded files with metadata and storage information.
    Supports images, documents, and other file types.
    """
    __tablename__ = "files"
    
    # File Information
    filename = Column(
        String(255),
        nullable=False,
        index=True,
        doc="Stored filename"
    )
    
    original_filename = Column(
        String(255),
        nullable=False,
        doc="Original uploaded filename"
    )
    
    content_type = Column(
        String(100),
        nullable=False,
        index=True,
        doc="MIME content type"
    )
    
    size = Column(
        Integer,
        nullable=False,
        doc="File size in bytes"
    )
    
    # Storage Information
    url = Column(
        String(500),
        nullable=False,
        doc="Public URL to access the file"
    )
    
    storage_path = Column(
        String(500),
        nullable=False,
        doc="Storage path on disk or cloud"
    )
    
    # File Integrity
    hash_md5 = Column(
        String(32),
        nullable=True,
        index=True,
        doc="MD5 hash of file content"
    )
    
    hash_sha256 = Column(
        String(64),
        nullable=True,
        index=True,
        doc="SHA256 hash of file content"
    )
    
    # Metadata and Description
    description = Column(
        Text,
        nullable=True,
        doc="File description"
    )
    
    tags = Column(
        JSON,
        default=list,
        nullable=True,
        doc="File tags for categorization"
    )
    
    extra_data = Column(
        JSON,
        default=dict,
        nullable=True,
        doc="Additional file metadata (dimensions, EXIF, etc.)"
    )
    
    # Usage Tracking
    download_count = Column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of times file has been downloaded"
    )
    
    last_accessed = Column(
        String(50),
        nullable=True,
        doc="Last access timestamp"
    )
    
    # Relationships (Optional associations)
    collection_id = Column(
        UUID(as_uuid=True),
        ForeignKey("collections.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Associated collection (if any)"
    )
    
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Associated product (if any)"
    )
    
    # Relationships
    collection: Mapped[Optional["Collection"]] = relationship(
        "Collection",
        back_populates="files"
    )
    
    product: Mapped[Optional["Product"]] = relationship(
        "Product",
        back_populates="files"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_file_content_type", "content_type"),
        Index("idx_file_size", "size"),
        Index("idx_file_collection", "collection_id"),
        Index("idx_file_product", "product_id"),
        Index("idx_file_created", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<File(filename='{self.filename}', content_type='{self.content_type}')>"
    
    @property
    def file_extension(self) -> str:
        """Get file extension from filename."""
        return self.original_filename.split('.')[-1].lower() if '.' in self.original_filename else ''
    
    @property
    def is_image(self) -> bool:
        """Check if file is an image."""
        return self.content_type.startswith('image/')
    
    @property
    def is_document(self) -> bool:
        """Check if file is a document."""
        document_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ]
        return self.content_type in document_types
    
    @property
    def human_readable_size(self) -> str:
        """Get human readable file size."""
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def get_tags_list(self) -> List[str]:
        """Get tags as list of strings."""
        if isinstance(self.tags, list):
            return self.tags
        return []
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the file."""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the file."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
