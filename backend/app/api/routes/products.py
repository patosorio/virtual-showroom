"""
Product API Routes

REST API endpoints for product management.
Handles CRUD operations, variants, images, specifications, and search.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.product.service import ProductService
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductSummaryResponse,
    ProductVariantCreate, ProductVariantUpdate, ProductVariantResponse,
    ProductImageCreate, ProductImageResponse, ProductImageUploadRequest,
    TechnicalSpecificationCreate, TechnicalSpecificationResponse,
    SizeChartCreate, SizeChartResponse,
    ProductListFilters, ProductSearchResult, ProductAnalytics,
    BulkProductImportRequest
)
from app.schemas.base import PaginatedResponse, BulkOperationResponse
from fastapi import HTTPException

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse[ProductSummaryResponse],
    summary="List products",
    description="Get a paginated list of products with optional filtering"
)
async def list_products(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    collection_id: Optional[UUID] = Query(None, description="Filter by collection"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    color: Optional[str] = Query(None, description="Filter by available color"),
    price_min: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    price_max: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    query: Optional[str] = Query(None, description="Search query"),
    has_variants: Optional[bool] = Query(None, description="Filter products with/without variants"),
    has_images: Optional[bool] = Query(None, description="Filter products with/without images"),
    order_by: Optional[str] = Query(None, description="Field to order by"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """List products with pagination and filtering."""
    try:
        service = ProductService(db)
        
        # Build filters
        filters = ProductListFilters(
            collection_id=collection_id,
            category=category,
            status=status,
            is_featured=is_featured,
            color=color,
            price_min=price_min,
            price_max=price_max,
            query=query,
            has_variants=has_variants,
            has_images=has_images
        )
        
        # Get products
        products, total = await service.list_products(
            filters=filters,
            skip=skip,
            limit=limit,
            order_by=order_by,
            user_id=UUID(current_user["uid"]) if current_user else None
        )
        
        # Convert to summary response models
        product_responses = [
            ProductSummaryResponse.model_validate(product)
            for product in products
        ]
        
        return PaginatedResponse.create(
            items=product_responses,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while listing products"
        )


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description="Create a new product with variants and specifications (admin only)"
)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new product."""
    try:
        service = ProductService(db)
        
        product = await service.create_product_with_variants(
            data=product_data,
            user_id=UUID(current_user["uid"])
        )
        
        return ProductResponse.model_validate(product)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the product"
        )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    description="Get a specific product with all details by its UUID"
)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get a product by ID with full details."""
    try:
        service = ProductService(db)
        
        product = await service.get_product_with_details(product_id)
        
        return ProductResponse.model_validate(product)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the product"
        )


@router.get(
    "/sku/{sku}",
    response_model=ProductResponse,
    summary="Get product by SKU",
    description="Get a specific product by its SKU"
)
async def get_product_by_sku(
    sku: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get a product by SKU."""
    try:
        service = ProductService(db)
        
        product = await service.get_product_by_sku(sku)
        
        return ProductResponse.model_validate(product)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the product"
        )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product",
    description="Update an existing product (admin only)"
)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a product."""
    try:
        service = ProductService(db)
        
        product = await service.update_product(
            product_id=product_id,
            data=product_data,
            user_id=UUID(current_user["uid"])
        )
        
        return ProductResponse.model_validate(product)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the product"
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product",
    description="Soft delete a product (admin only)"
)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a product."""
    try:
        service = ProductService(db)
        
        await service.delete(
            id=product_id,
            user_id=UUID(current_user["uid"])
        )
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the product"
        )


@router.get(
    "/collection/{collection_id}",
    response_model=List[ProductSummaryResponse],
    summary="Get products by collection",
    description="Get all products in a specific collection"
)
async def get_products_by_collection(
    collection_id: UUID,
    include_inactive: bool = Query(False, description="Include inactive products"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of items to return"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get products by collection."""
    try:
        service = ProductService(db)
        
        products = await service.get_products_by_collection(
            collection_id=collection_id,
            include_inactive=include_inactive,
            skip=skip,
            limit=limit
        )
        
        return [
            ProductSummaryResponse.model_validate(product)
            for product in products
        ]
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving products"
        )


@router.get(
    "/featured/",
    response_model=List[ProductSummaryResponse],
    summary="Get featured products",
    description="Get products marked as featured"
)
async def get_featured_products(
    limit: int = Query(10, ge=1, le=50, description="Number of products to return"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get featured products."""
    try:
        service = ProductService(db)
        
        products = await service.get_featured_products(limit=limit)
        
        return [
            ProductSummaryResponse.model_validate(product)
            for product in products
        ]
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving featured products"
        )


@router.get(
    "/search/",
    response_model=List[ProductSummaryResponse],
    summary="Search products",
    description="Search products by name, description, or SKU"
)
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    collection_id: Optional[UUID] = Query(None, description="Filter by collection"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Search products."""
    try:
        service = ProductService(db)
        
        products = await service.search_products(
            query=q,
            category=category,
            collection_id=collection_id,
            skip=skip,
            limit=limit
        )
        
        return [
            ProductSummaryResponse.model_validate(product)
            for product in products
        ]
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while searching products"
        )


# Product Status Management

@router.patch(
    "/{product_id}/status",
    response_model=ProductResponse,
    summary="Update product status",
    description="Update product status (admin only)"
)
async def update_product_status(
    product_id: UUID,
    status: str = Query(..., description="New status (active, discontinued, coming_soon)"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update product status."""
    try:
        service = ProductService(db)
        
        product = await service.update_product_status(
            product_id=product_id,
            status=status,
            user_id=UUID(current_user["uid"])
        )
        
        return ProductResponse.model_validate(product)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating product status"
        )


@router.patch(
    "/{product_id}/featured",
    response_model=ProductResponse,
    summary="Toggle featured status",
    description="Toggle product featured status (admin only)"
)
async def toggle_featured_status(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Toggle product featured status."""
    try:
        service = ProductService(db)
        
        product = await service.toggle_featured_status(
            product_id=product_id,
            user_id=UUID(current_user["uid"])
        )
        
        return ProductResponse.model_validate(product)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating featured status"
        )


# Product Variants

@router.post(
    "/{product_id}/variants",
    response_model=ProductVariantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add product variant",
    description="Add a new variant to a product (admin only)"
)
async def add_product_variant(
    product_id: UUID,
    variant_data: ProductVariantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add a variant to a product."""
    try:
        service = ProductService(db)
        
        variant = await service.add_product_variant(
            product_id=product_id,
            variant_data=variant_data,
            user_id=UUID(current_user["uid"])
        )
        
        return ProductVariantResponse.model_validate(variant)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the variant"
        )


@router.put(
    "/variants/{variant_id}",
    response_model=ProductVariantResponse,
    summary="Update product variant",
    description="Update a product variant (admin only)"
)
async def update_product_variant(
    variant_id: UUID,
    variant_data: ProductVariantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a product variant."""
    try:
        service = ProductService(db)
        
        variant = await service.update_product_variant(
            variant_id=variant_id,
            variant_data=variant_data,
            user_id=UUID(current_user["uid"])
        )
        
        return ProductVariantResponse.model_validate(variant)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the variant"
        )


# Product Images

@router.post(
    "/{product_id}/images",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload product image",
    description="Upload an image for a product (admin only)"
)
async def upload_product_image(
    product_id: UUID,
    file: UploadFile = File(...),
    variant_id: Optional[UUID] = Form(None),
    alt_text: Optional[str] = Form(None),
    image_type: str = Form("gallery"),
    sort_order: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload an image for a product."""
    try:
        # This would integrate with the file service
        # For now, create a placeholder image record
        service = ProductService(db)
        
        # Create image data (would normally come from file service)
        image_data = ProductImageCreate(
            filename=file.filename,
            original_filename=file.filename,
            url=f"/images/{file.filename}",  # Placeholder URL
            alt_text=alt_text,
            type=image_type,
            sort_order=sort_order or 0,
            variant_id=variant_id
        )
        
        image = await service.add_product_image(
            product_id=product_id,
            image_data=image_data,
            user_id=UUID(current_user["uid"])
        )
        
        return ProductImageResponse.model_validate(image)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while uploading the image"
        )


# Technical Specifications

@router.post(
    "/{product_id}/specifications",
    response_model=TechnicalSpecificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add technical specification",
    description="Add a technical specification to a product (admin only)"
)
async def add_technical_specification(
    product_id: UUID,
    spec_data: TechnicalSpecificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add a technical specification to a product."""
    try:
        service = ProductService(db)
        
        specification = await service.add_technical_specification(
            product_id=product_id,
            spec_data=spec_data,
            user_id=UUID(current_user["uid"])
        )
        
        return TechnicalSpecificationResponse.model_validate(specification)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the specification"
        )


# Size Charts

@router.post(
    "/{product_id}/size-chart",
    response_model=SizeChartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create size chart",
    description="Create a size chart for a product (admin only)"
)
async def create_size_chart(
    product_id: UUID,
    size_chart_data: SizeChartCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a size chart for a product."""
    try:
        service = ProductService(db)
        
        size_chart = await service.create_size_chart(
            product_id=product_id,
            size_chart_data=size_chart_data,
            user_id=UUID(current_user["uid"])
        )
        
        return SizeChartResponse.model_validate(size_chart)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the size chart"
        )


# Analytics

@router.get(
    "/{product_id}/analytics",
    response_model=ProductAnalytics,
    summary="Get product analytics",
    description="Get detailed analytics for a product (admin only)"
)
async def get_product_analytics(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get analytics for a product."""
    try:
        service = ProductService(db)
        
        analytics = await service.get_product_analytics(product_id)
        
        return analytics
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving analytics"
        )


# Bulk Operations

@router.post(
    "/bulk/import",
    response_model=BulkOperationResponse,
    summary="Bulk import products",
    description="Import multiple products in bulk (admin only)"
)
async def bulk_import_products(
    import_data: BulkProductImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Bulk import products."""
    try:
        # This would be implemented with actual bulk import logic
        # For now, return a placeholder response
        
        return BulkOperationResponse(
            success_count=0,
            error_count=0,
            total_count=len(import_data.products),
            errors=[]
        )
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during bulk import"
        )
