"""
Admin Pydantic Schemas

Schemas for admin-specific operations, analytics, and management features.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from pydantic import Field, field_validator

from .base import BaseSchema, PaginatedResponse


# Dashboard Schemas

class DashboardStats(BaseSchema):
    """Main dashboard statistics."""
    
    collections: "CollectionStats"
    products: "ProductStats"
    files: "FileStats"
    users: "UserStats"
    system: "SystemStats"


class CollectionStats(BaseSchema):
    """Collection statistics for dashboard."""
    
    total: int = Field(description="Total number of collections")
    published: int = Field(description="Number of published collections")
    draft: int = Field(description="Number of draft collections")
    archived: int = Field(description="Number of archived collections")
    recent_additions: int = Field(description="Collections added in last 30 days")
    by_season: Dict[str, int] = Field(description="Collections grouped by season")
    by_year: Dict[str, int] = Field(description="Collections grouped by year")
    average_products_per_collection: float = Field(description="Average products per collection")


class ProductStats(BaseSchema):
    """Product statistics for dashboard."""
    
    total: int = Field(description="Total number of products")
    active: int = Field(description="Number of active products")
    discontinued: int = Field(description="Number of discontinued products")
    coming_soon: int = Field(description="Number of coming soon products")
    featured: int = Field(description="Number of featured products")
    recent_additions: int = Field(description="Products added in last 30 days")
    by_category: Dict[str, int] = Field(description="Products grouped by category")
    with_variants: int = Field(description="Products with variants")
    with_images: int = Field(description="Products with images")
    with_specifications: int = Field(description="Products with technical specifications")
    average_price: Optional[float] = Field(None, description="Average product price")
    price_distribution: Dict[str, int] = Field(description="Price range distribution")


class FileStats(BaseSchema):
    """File statistics for dashboard."""
    
    total: int = Field(description="Total number of files")
    total_size: int = Field(description="Total file size in bytes")
    total_size_human: str = Field(description="Human readable total size")
    by_type: Dict[str, int] = Field(description="Files grouped by content type")
    images: int = Field(description="Number of image files")
    documents: int = Field(description="Number of document files")
    recent_uploads: int = Field(description="Files uploaded in last 30 days")
    average_file_size: float = Field(description="Average file size in bytes")
    largest_files: List[Dict[str, Any]] = Field(description="Largest files information")


class UserStats(BaseSchema):
    """User statistics for dashboard."""
    
    total: int = Field(description="Total number of users")
    active: int = Field(description="Number of active users")
    inactive: int = Field(description="Number of inactive users")
    by_role: Dict[str, int] = Field(description="Users grouped by role")
    recent_registrations: int = Field(description="Users registered in last 30 days")
    recent_logins: int = Field(description="Users logged in last 30 days")
    average_login_frequency: float = Field(description="Average logins per user per month")


class SystemStats(BaseSchema):
    """System statistics for dashboard."""
    
    database_size: int = Field(description="Database size in bytes")
    database_size_human: str = Field(description="Human readable database size")
    storage_used: int = Field(description="Storage used in bytes")
    storage_used_human: str = Field(description="Human readable storage used")
    storage_available: int = Field(description="Available storage in bytes")
    storage_available_human: str = Field(description="Human readable available storage")
    backup_status: str = Field(description="Last backup status")
    last_backup: Optional[datetime] = Field(None, description="Last backup timestamp")
    uptime: float = Field(description="System uptime in seconds")
    uptime_human: str = Field(description="Human readable uptime")
    version: str = Field(description="Application version")
    environment: str = Field(description="Environment (development, staging, production)")


# Analytics Schemas

class TimeSeriesData(BaseSchema):
    """Time series data point."""
    
    date: date
    value: Union[int, float]
    label: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AnalyticsDateRange(BaseSchema):
    """Date range for analytics queries."""
    
    start_date: date = Field(description="Start date for analytics")
    end_date: date = Field(description="End date for analytics")
    granularity: str = Field(
        default="day",
        description="Data granularity",
        examples=["hour", "day", "week", "month"]
    )
    
    @field_validator('granularity')
    @classmethod
    def validate_granularity(cls, v: str) -> str:
        """Validate granularity value."""
        valid_values = ["hour", "day", "week", "month", "quarter", "year"]
        if v not in valid_values:
            raise ValueError(f"Granularity must be one of: {', '.join(valid_values)}")
        return v
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v: date, info) -> date:
        """Validate that end date is after start date."""
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError("End date must be after start date")
        return v


class CollectionAnalytics(BaseSchema):
    """Detailed collection analytics."""
    
    collection_id: UUID
    collection_name: str
    collection_slug: str
    total_products: int
    product_categories: Dict[str, int]
    average_product_price: Optional[float]
    price_range: Dict[str, float]
    total_variants: int
    total_images: int
    creation_timeline: List[TimeSeriesData]
    popularity_score: float = Field(description="Collection popularity score based on various metrics")
    completion_percentage: float = Field(description="Percentage of products with complete data")


class ProductAnalytics(BaseSchema):
    """Detailed product analytics."""
    
    product_id: UUID
    product_name: str
    product_sku: str
    collection_name: str
    total_variants: int
    total_images: int
    specifications_count: int
    has_size_chart: bool
    creation_date: date
    last_updated: date
    completion_score: float = Field(description="Product data completion score")
    image_quality_score: float = Field(description="Image quality assessment score")
    seo_score: float = Field(description="SEO optimization score")


class UserActivityAnalytics(BaseSchema):
    """User activity analytics."""
    
    user_id: UUID
    user_email: str
    role: str
    total_logins: int
    last_login: Optional[datetime]
    login_frequency: List[TimeSeriesData]
    collections_created: int
    products_created: int
    files_uploaded: int
    activity_score: float = Field(description="User activity score")


class PerformanceAnalytics(BaseSchema):
    """System performance analytics."""
    
    response_times: List[TimeSeriesData]
    request_volume: List[TimeSeriesData]
    error_rates: List[TimeSeriesData]
    database_performance: Dict[str, Any]
    storage_growth: List[TimeSeriesData]
    peak_usage_times: List[str]
    slowest_endpoints: List[Dict[str, Any]]


# Bulk Operations Schemas

class BulkImportRequest(BaseSchema):
    """Request schema for bulk import operations."""
    
    import_type: str = Field(..., description="Type of import (products, collections, etc.)")
    file_url: Optional[str] = Field(None, description="URL of file to import")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Direct data to import")
    options: Optional[Dict[str, Any]] = Field(None, description="Import options")
    update_existing: bool = Field(default=False, description="Whether to update existing records")
    validate_only: bool = Field(default=False, description="Only validate, don't import")
    
    @field_validator('import_type')
    @classmethod
    def validate_import_type(cls, v: str) -> str:
        """Validate import type."""
        valid_types = ["products", "collections", "users", "files"]
        if v not in valid_types:
            raise ValueError(f"Import type must be one of: {', '.join(valid_types)}")
        return v


class BulkImportResponse(BaseSchema):
    """Response schema for bulk import operations."""
    
    import_id: UUID = Field(description="Import operation ID")
    status: str = Field(description="Import status")
    total_records: int = Field(description="Total records to import")
    processed_records: int = Field(description="Records processed so far")
    successful_records: int = Field(description="Successfully imported records")
    failed_records: int = Field(description="Failed import records")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Import errors")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="Import warnings")
    started_at: datetime = Field(description="Import start time")
    completed_at: Optional[datetime] = Field(None, description="Import completion time")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")


class BulkExportRequest(BaseSchema):
    """Request schema for bulk export operations."""
    
    export_type: str = Field(..., description="Type of export")
    format: str = Field(default="csv", description="Export format")
    filters: Optional[Dict[str, Any]] = Field(None, description="Export filters")
    fields: Optional[List[str]] = Field(None, description="Specific fields to export")
    include_relationships: bool = Field(default=True, description="Include related data")
    
    @field_validator('export_type')
    @classmethod
    def validate_export_type(cls, v: str) -> str:
        """Validate export type."""
        valid_types = ["products", "collections", "users", "files", "analytics"]
        if v not in valid_types:
            raise ValueError(f"Export type must be one of: {', '.join(valid_types)}")
        return v
    
    @field_validator('format')
    @classmethod
    def validate_export_format(cls, v: str) -> str:
        """Validate export format."""
        valid_formats = ["csv", "xlsx", "json", "xml"]
        if v not in valid_formats:
            raise ValueError(f"Export format must be one of: {', '.join(valid_formats)}")
        return v


class BulkExportResponse(BaseSchema):
    """Response schema for bulk export operations."""
    
    export_id: UUID = Field(description="Export operation ID")
    status: str = Field(description="Export status")
    file_url: Optional[str] = Field(None, description="Download URL for completed export")
    total_records: int = Field(description="Total records exported")
    file_size: Optional[int] = Field(None, description="Export file size in bytes")
    created_at: datetime = Field(description="Export creation time")
    expires_at: Optional[datetime] = Field(None, description="Download link expiration")


# System Management Schemas

class SystemHealthCheck(BaseSchema):
    """System health check response."""
    
    status: str = Field(description="Overall system status")
    database: Dict[str, Any] = Field(description="Database health status")
    storage: Dict[str, Any] = Field(description="Storage health status")
    external_services: Dict[str, Any] = Field(description="External services status")
    performance_metrics: Dict[str, Any] = Field(description="Performance metrics")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Active alerts")
    last_check: datetime = Field(description="Last health check timestamp")


class SystemConfiguration(BaseSchema):
    """System configuration schema."""
    
    feature_flags: Dict[str, bool] = Field(description="Feature flag settings")
    limits: Dict[str, int] = Field(description="System limits")
    integrations: Dict[str, Dict[str, Any]] = Field(description="Integration settings")
    security_settings: Dict[str, Any] = Field(description="Security configuration")
    performance_settings: Dict[str, Any] = Field(description="Performance tuning settings")


class SystemConfigurationUpdate(BaseSchema):
    """System configuration update schema."""
    
    feature_flags: Optional[Dict[str, bool]] = Field(None, description="Feature flag updates")
    limits: Optional[Dict[str, int]] = Field(None, description="System limit updates")
    integrations: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="Integration updates")
    security_settings: Optional[Dict[str, Any]] = Field(None, description="Security setting updates")
    performance_settings: Optional[Dict[str, Any]] = Field(None, description="Performance setting updates")


class BackupRequest(BaseSchema):
    """Backup request schema."""
    
    backup_type: str = Field(default="full", description="Type of backup")
    include_files: bool = Field(default=True, description="Include uploaded files")
    compression: bool = Field(default=True, description="Enable compression")
    encryption: bool = Field(default=True, description="Enable encryption")
    
    @field_validator('backup_type')
    @classmethod
    def validate_backup_type(cls, v: str) -> str:
        """Validate backup type."""
        valid_types = ["full", "incremental", "differential", "database_only"]
        if v not in valid_types:
            raise ValueError(f"Backup type must be one of: {', '.join(valid_types)}")
        return v


class BackupResponse(BaseSchema):
    """Backup response schema."""
    
    backup_id: UUID = Field(description="Backup operation ID")
    status: str = Field(description="Backup status")
    backup_type: str = Field(description="Type of backup")
    file_size: Optional[int] = Field(None, description="Backup file size in bytes")
    created_at: datetime = Field(description="Backup creation time")
    completed_at: Optional[datetime] = Field(None, description="Backup completion time")
    download_url: Optional[str] = Field(None, description="Backup download URL")
    retention_until: Optional[datetime] = Field(None, description="Backup retention expiry")


class MaintenanceMode(BaseSchema):
    """Maintenance mode configuration."""
    
    enabled: bool = Field(description="Whether maintenance mode is enabled")
    message: Optional[str] = Field(None, description="Maintenance message for users")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")
    allowed_ips: Optional[List[str]] = Field(None, description="IP addresses allowed during maintenance")
    start_time: Optional[datetime] = Field(None, description="Maintenance start time")
    end_time: Optional[datetime] = Field(None, description="Maintenance end time")


class AuditLogEntry(BaseSchema):
    """Audit log entry schema."""
    
    id: UUID
    timestamp: datetime
    user_id: Optional[UUID]
    user_email: Optional[str]
    action: str = Field(description="Action performed")
    resource_type: str = Field(description="Type of resource affected")
    resource_id: Optional[UUID] = Field(None, description="ID of affected resource")
    ip_address: Optional[str] = Field(None, description="User IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    changes: Optional[Dict[str, Any]] = Field(None, description="Changes made")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AuditLogFilters(BaseSchema):
    """Filters for audit log queries."""
    
    user_id: Optional[UUID] = Field(None, description="Filter by user")
    action: Optional[str] = Field(None, description="Filter by action")
    resource_type: Optional[str] = Field(None, description="Filter by resource type")
    resource_id: Optional[UUID] = Field(None, description="Filter by resource ID")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")
    ip_address: Optional[str] = Field(None, description="Filter by IP address")


# Forward reference rebuilding
CollectionStats.model_rebuild()
ProductStats.model_rebuild()
FileStats.model_rebuild()
UserStats.model_rebuild()
SystemStats.model_rebuild()
DashboardStats.model_rebuild()
