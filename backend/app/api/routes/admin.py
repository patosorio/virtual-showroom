"""
Admin API Routes

REST API endpoints for admin operations, analytics, and system management.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_admin_user
from app.services.admin import AdminService
from app.schemas.admin import (
    DashboardStats, AnalyticsDateRange,
    BulkImportRequest, BulkImportResponse,
    BulkExportRequest, BulkExportResponse,
    SystemHealthCheck, AuditLogEntry, AuditLogFilters
)
from app.schemas.base import PaginatedResponse
from fastapi import HTTPException

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=DashboardStats,
    summary="Get dashboard statistics",
    description="Get comprehensive dashboard statistics (admin only)"
)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """Get dashboard statistics."""
    try:
        service = AdminService(db)
        
        stats = await service.get_dashboard_stats()
        
        return stats
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving dashboard statistics"
        )


@router.get(
    "/analytics/collections",
    response_model=List[dict],
    summary="Get collection analytics",
    description="Get detailed collection analytics (admin only)"
)
async def get_collection_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    granularity: str = Query("day", description="Data granularity"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """Get collection analytics."""
    try:
        service = AdminService(db)
        
        date_range = None
        if start_date and end_date:
            date_range = AnalyticsDateRange(
                start_date=start_date,
                end_date=end_date,
                granularity=granularity
            )
        
        analytics = await service.get_collection_analytics(date_range)
        
        return analytics
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving collection analytics"
        )


@router.get(
    "/analytics/products",
    response_model=List[dict],
    summary="Get product analytics",
    description="Get detailed product analytics (admin only)"
)
async def get_product_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    granularity: str = Query("day", description="Data granularity"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """Get product analytics."""
    try:
        service = AdminService(db)
        
        date_range = None
        if start_date and end_date:
            date_range = AnalyticsDateRange(
                start_date=start_date,
                end_date=end_date,
                granularity=granularity
            )
        
        analytics = await service.get_product_analytics(date_range)
        
        return analytics
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving product analytics"
        )


@router.post(
    "/bulk/import",
    response_model=BulkImportResponse,
    summary="Bulk import data",
    description="Import data in bulk (admin only)"
)
async def bulk_import_data(
    import_request: BulkImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """Bulk import data."""
    try:
        service = AdminService(db)
        
        result = await service.bulk_import_data(
            import_request=import_request,
            admin_user_id=UUID(current_user["uid"])
        )
        
        return result
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during bulk import"
        )


@router.post(
    "/bulk/export",
    response_model=BulkExportResponse,
    summary="Bulk export data",
    description="Export data in bulk (admin only)"
)
async def bulk_export_data(
    export_request: BulkExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """Bulk export data."""
    try:
        service = AdminService(db)
        
        result = await service.bulk_export_data(
            export_request=export_request,
            admin_user_id=UUID(current_user["uid"])
        )
        
        return result
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during bulk export"
        )


@router.get(
    "/health",
    response_model=SystemHealthCheck,
    summary="Get system health",
    description="Get system health status (admin only)"
)
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """Get system health status."""
    try:
        service = AdminService(db)
        
        health = await service.get_system_health()
        
        return health
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while checking system health"
        )


@router.get(
    "/audit-logs",
    response_model=PaginatedResponse[AuditLogEntry],
    summary="Get audit logs",
    description="Get audit logs with filtering (admin only)"
)
async def get_audit_logs(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of items to return"),
    user_id: Optional[UUID] = Query(None, description="Filter by user"),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[UUID] = Query(None, description="Filter by resource ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """Get audit logs."""
    try:
        # This would integrate with an audit logging system
        # For now, return empty response
        
        return PaginatedResponse.create(
            items=[],
            total=0,
            skip=skip,
            limit=limit
        )
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving audit logs"
        )
