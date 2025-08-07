"""
API Routes Package

Exports all route modules for the FastAPI application.
"""

# Import all route modules
from . import collections
from . import products
from . import auth
from . import files
from . import admin

__all__ = [
    "collections",
    "products", 
    "auth",
    "files",
    "admin",
]
