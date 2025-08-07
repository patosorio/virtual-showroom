"""
Models Package

Exports all database models for the application.
"""

# Import base model
from .base import BaseModel

# Import all models to ensure they're registered with SQLAlchemy
from .user import User
from .collection import Collection
from .file import File

# Import product models
from .product.product import Product
from .product.variant import ProductVariant
from .product.image import ProductImage
from .product.technical_specification import TechnicalSpecification
from .product.technical_drawing import TechnicalDrawing
from .product.size_chart import SizeChart

__all__ = [
    # Base
    "BaseModel",
    
    # Core models
    "User",
    "Collection", 
    "File",
    
    # Product models
    "Product",
    "ProductVariant",
    "ProductImage",
    "TechnicalSpecification",
    "TechnicalDrawing",
    "SizeChart",
]
