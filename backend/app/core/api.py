"""
Main API router that includes all application routes.
"""

from fastapi import APIRouter

# Create the main API router
router = APIRouter()

# TODO: Include all route modules here when they are created
# from ..api.routes import collections, products, auth, files, admin
# 
# router.include_router(collections.router, prefix="/collections", tags=["Collections"])
# router.include_router(products.router, prefix="/products", tags=["Products"])
# router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# router.include_router(files.router, prefix="/files", tags=["Files"])
# router.include_router(admin.router, prefix="/admin", tags=["Admin"])