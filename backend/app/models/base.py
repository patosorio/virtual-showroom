"""
Base Database Model

Provides common fields and functionality for all database models.
Includes audit fields, soft deletion, and UUID primary keys.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.sql import func


@as_declarative()
class Base:
    """Base class for all database models."""
    
    id: Any
    __name__: str
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"


class BaseModel(Base):
    """
    Abstract base model with common fields.
    
    Provides:
    - UUID primary key
    - Created/updated timestamps
    - Soft deletion support
    - Created by user tracking
    """
    __abstract__ = True
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique identifier"
    )
    
    # Audit fields
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Record creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Record last update timestamp"
    )
    
    # User tracking
    created_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        doc="ID of user who created this record"
    )
    
    updated_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        doc="ID of user who last updated this record"
    )
    
    # Soft deletion
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Soft deletion flag"
    )
    
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Soft deletion timestamp"
    )
    
    # Additional metadata
    notes = Column(
        Text,
        nullable=True,
        doc="Optional notes or comments"
    )
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def soft_delete(self, user_id: uuid.UUID = None) -> None:
        """
        Perform soft deletion of the record.
        
        Args:
            user_id: ID of user performing the deletion
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.updated_by = user_id
    
    def restore(self, user_id: uuid.UUID = None) -> None:
        """
        Restore a soft-deleted record.
        
        Args:
            user_id: ID of user performing the restoration
        """
        self.is_deleted = False
        self.deleted_at = None
        self.updated_by = user_id