"""
Repositories Package

Exports all repository classes for data access layer.
"""

# Base repository
from .base import BaseRepository

# Collection repository
from .collection import CollectionRepository

# Product repositories
from .product.repository import (
    ProductRepository,
    ProductVariantRepository,
    ProductImageRepository,
    TechnicalSpecificationRepository,
    SizeChartRepository,
)

# File repository
from .file import FileRepository

# User repository
from .user import UserRepository

__all__ = [
    # Base
    "BaseRepository",
    
    # Collections
    "CollectionRepository",
    
    # Products
    "ProductRepository",
    "ProductVariantRepository", 
    "ProductImageRepository",
    "TechnicalSpecificationRepository",
    "SizeChartRepository",
    
    # Files
    "FileRepository",
    
    # Users
    "UserRepository",
]
