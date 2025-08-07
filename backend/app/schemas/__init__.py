"""
Pydantic Schemas Package

Exports all schemas for request/response serialization, validation, and documentation.
"""

# Base schemas
from .base import (
    BaseSchema,
    BaseResponseSchema,
    BaseCreateSchema,
    BaseUpdateSchema,
    PaginationParams,
    PaginatedResponse,
    SearchParams,
    FileResponse,
    BulkOperationResponse,
    ErrorDetail,
    ErrorResponse,
    StatusEnum,
    validate_slug,
    validate_url,
    validate_currency,
    get_name_field,
    get_slug_field,
    get_description_field,
    get_short_description_field,
    get_price_field,
)

# Collection schemas
from .collection import (
    CollectionBase,
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionSummary,
    CollectionListFilters,
    CollectionPublishRequest,
    CollectionAnalytics,
)

# Product schemas
from .product import (
    # Product variants
    ProductVariantBase,
    ProductVariantCreate,
    ProductVariantUpdate,
    ProductVariantResponse,
    
    # Product images
    ProductImageBase,
    ProductImageCreate,
    ProductImageUpdate,
    ProductImageResponse,
    
    # Technical specifications
    TechnicalSpecificationBase,
    TechnicalSpecificationCreate,
    TechnicalSpecificationUpdate,
    TechnicalSpecificationResponse,
    
    # Size charts
    SizeChartEntryBase,
    SizeChartBase,
    SizeChartCreate,
    SizeChartUpdate,
    SizeChartResponse,
    
    # Main product schemas
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductSummaryResponse,
    ProductListFilters,
    ProductSearchResult,
    ProductAnalytics,
    
    # File upload schemas
    ProductImageUploadRequest,
    BulkProductImportItem,
    BulkProductImportRequest,
)

# Authentication schemas
from .auth import (
    # Authentication
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest,
    
    # User management
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfile,
    UserProfileUpdate,
    
    # Permissions and roles
    PermissionSchema,
    RoleSchema,
    UserRoleUpdate,
    
    # Sessions and tokens
    ActiveSession,
    TokenValidationResponse,
    
    # Password and security
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    
    # Two-factor authentication
    TwoFactorSetupRequest,
    TwoFactorVerifyRequest,
    TwoFactorBackupCodes,
    
    # API key management
    APIKeyCreate,
    APIKeyResponse,
    APIKeyUpdate,
)

# File schemas
from .file import (
    # File base schemas
    FileBase,
    FileCreate,
    FileUpdate,
    FileResponse,
    
    # File upload schemas
    FileUploadRequest,
    FileUploadResponse,
    MultipleFileUploadRequest,
    MultipleFileUploadResponse,
    
    # Image processing schemas
    ImageDimensions,
    ImageMetadata,
    ThumbnailResponse,
    ImageProcessingRequest,
    ImageProcessingResponse,
    
    # Document processing schemas
    DocumentMetadata,
    DocumentProcessingRequest,
    DocumentProcessingResponse,
    
    # File management schemas
    FileListFilters,
    FileBatchOperation,
    FileBatchOperationResponse,
    FileAnalytics,
    FileStorageInfo,
)

# Admin schemas
from .admin import (
    # Dashboard schemas
    DashboardStats,
    CollectionStats,
    ProductStats,
    FileStats,
    UserStats,
    SystemStats,
    
    # Analytics schemas
    TimeSeriesData,
    AnalyticsDateRange,
    CollectionAnalytics,
    ProductAnalytics,
    UserActivityAnalytics,
    PerformanceAnalytics,
    
    # Bulk operations schemas
    BulkImportRequest,
    BulkImportResponse,
    BulkExportRequest,
    BulkExportResponse,
    
    # System management schemas
    SystemHealthCheck,
    SystemConfiguration,
    SystemConfigurationUpdate,
    BackupRequest,
    BackupResponse,
    MaintenanceMode,
    AuditLogEntry,
    AuditLogFilters,
)

__all__ = [
    # Base schemas
    "BaseSchema",
    "BaseResponseSchema", 
    "BaseCreateSchema",
    "BaseUpdateSchema",
    "PaginationParams",
    "PaginatedResponse",
    "SearchParams",
    "FileResponse",
    "BulkOperationResponse",
    "ErrorDetail",
    "ErrorResponse",
    "StatusEnum",
    "validate_slug",
    "validate_url", 
    "validate_currency",
    "get_name_field",
    "get_slug_field",
    "get_description_field",
    "get_short_description_field",
    "get_price_field",
    
    # Collection schemas
    "CollectionBase",
    "CollectionCreate",
    "CollectionUpdate", 
    "CollectionResponse",
    "CollectionSummary",
    "CollectionListFilters",
    "CollectionPublishRequest",
    "CollectionAnalytics",
    
    # Product schemas
    "ProductVariantBase",
    "ProductVariantCreate",
    "ProductVariantUpdate",
    "ProductVariantResponse",
    "ProductImageBase",
    "ProductImageCreate", 
    "ProductImageUpdate",
    "ProductImageResponse",
    "TechnicalSpecificationBase",
    "TechnicalSpecificationCreate",
    "TechnicalSpecificationUpdate",
    "TechnicalSpecificationResponse",
    "SizeChartEntryBase",
    "SizeChartBase",
    "SizeChartCreate",
    "SizeChartUpdate",
    "SizeChartResponse",
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductSummaryResponse",
    "ProductListFilters",
    "ProductSearchResult",
    "ProductAnalytics",
    "ProductImageUploadRequest",
    "BulkProductImportItem",
    "BulkProductImportRequest",
    
    # Authentication schemas
    "LoginRequest",
    "LoginResponse",
    "RefreshTokenRequest", 
    "RefreshTokenResponse",
    "LogoutRequest",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    "UserProfileUpdate",
    "PermissionSchema",
    "RoleSchema",
    "UserRoleUpdate",
    "ActiveSession",
    "TokenValidationResponse",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "PasswordChangeRequest",
    "TwoFactorSetupRequest",
    "TwoFactorVerifyRequest",
    "TwoFactorBackupCodes",
    "APIKeyCreate",
    "APIKeyResponse",
    "APIKeyUpdate",
    
    # File schemas
    "FileBase",
    "FileCreate",
    "FileUpdate",
    "FileResponse",
    "FileUploadRequest",
    "FileUploadResponse",
    "MultipleFileUploadRequest",
    "MultipleFileUploadResponse",
    "ImageDimensions",
    "ImageMetadata",
    "ThumbnailResponse",
    "ImageProcessingRequest",
    "ImageProcessingResponse",
    "DocumentMetadata",
    "DocumentProcessingRequest",
    "DocumentProcessingResponse",
    "FileListFilters",
    "FileBatchOperation",
    "FileBatchOperationResponse",
    "FileAnalytics",
    "FileStorageInfo",
    
    # Admin schemas
    "DashboardStats",
    "CollectionStats",
    "ProductStats",
    "FileStats",
    "UserStats",
    "SystemStats",
    "TimeSeriesData",
    "AnalyticsDateRange",
    "CollectionAnalytics",
    "ProductAnalytics",
    "UserActivityAnalytics",
    "PerformanceAnalytics",
    "BulkImportRequest",
    "BulkImportResponse",
    "BulkExportRequest",
    "BulkExportResponse",
    "SystemHealthCheck",
    "SystemConfiguration",
    "SystemConfigurationUpdate",
    "BackupRequest",
    "BackupResponse",
    "MaintenanceMode",
    "AuditLogEntry",
    "AuditLogFilters",
]
