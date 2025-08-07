"""
File Management Pydantic Schemas

Schemas for file uploads, management, and metadata.
"""

from typing import Optional, List, Dict, Any, Union
from uuid import UUID

from pydantic import Field, field_validator

from .base import BaseSchema, BaseResponseSchema, BaseCreateSchema, BaseUpdateSchema


# File Base Schemas

class FileBase(BaseSchema):
    """Base schema for files."""
    
    filename: str = Field(..., min_length=1, max_length=255, description="File name")
    original_filename: str = Field(..., description="Original uploaded filename")
    content_type: str = Field(..., description="MIME content type")
    size: int = Field(..., gt=0, description="File size in bytes")
    description: Optional[str] = Field(None, max_length=500, description="File description")
    tags: Optional[List[str]] = Field(default_factory=list, description="File tags")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        """Validate content type format."""
        if '/' not in v:
            raise ValueError("Content type must be in format 'type/subtype'")
        return v.lower()
    
    @field_validator('size')
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """Validate file size limits."""
        # 100MB max file size
        max_size = 100 * 1024 * 1024
        if v > max_size:
            raise ValueError(f"File size cannot exceed {max_size} bytes (100MB)")
        return v


class FileCreate(FileBase, BaseCreateSchema):
    """Schema for creating file records."""
    
    url: str = Field(..., description="File URL")
    storage_path: str = Field(..., description="Storage path")
    hash_md5: Optional[str] = Field(None, description="MD5 hash of file content")
    hash_sha256: Optional[str] = Field(None, description="SHA256 hash of file content")
    
    # Optional relationships
    collection_id: Optional[UUID] = Field(None, description="Associated collection")
    product_id: Optional[UUID] = Field(None, description="Associated product")
    
    @field_validator('hash_md5')
    @classmethod
    def validate_md5_hash(cls, v: Optional[str]) -> Optional[str]:
        """Validate MD5 hash format."""
        if v and len(v) != 32:
            raise ValueError("MD5 hash must be 32 characters long")
        return v
    
    @field_validator('hash_sha256')
    @classmethod
    def validate_sha256_hash(cls, v: Optional[str]) -> Optional[str]:
        """Validate SHA256 hash format."""
        if v and len(v) != 64:
            raise ValueError("SHA256 hash must be 64 characters long")
        return v


class FileUpdate(BaseUpdateSchema):
    """Schema for updating file records."""
    
    filename: Optional[str] = Field(None, min_length=1, max_length=255, description="File name")
    description: Optional[str] = Field(None, max_length=500, description="File description")
    tags: Optional[List[str]] = Field(None, description="File tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    collection_id: Optional[UUID] = Field(None, description="Associated collection")
    product_id: Optional[UUID] = Field(None, description="Associated product")


class FileResponse(FileBase, BaseResponseSchema):
    """Schema for file response."""
    
    url: str
    storage_path: str
    hash_md5: Optional[str]
    hash_sha256: Optional[str]
    download_count: int = Field(default=0, description="Number of downloads")
    last_accessed: Optional[str] = Field(None, description="Last access timestamp")
    
    # Relationships
    collection_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    collection: Optional["CollectionSummary"] = None
    product: Optional["ProductSummaryResponse"] = None
    
    # Computed fields
    file_extension: str = Field(description="File extension")
    is_image: bool = Field(description="Whether file is an image")
    is_document: bool = Field(description="Whether file is a document")
    human_readable_size: str = Field(description="Human readable file size")


# File Upload Schemas

class FileUploadRequest(BaseSchema):
    """Request schema for file upload."""
    
    description: Optional[str] = Field(None, max_length=500, description="File description")
    tags: Optional[List[str]] = Field(default_factory=list, description="File tags")
    collection_id: Optional[UUID] = Field(None, description="Associate with collection")
    product_id: Optional[UUID] = Field(None, description="Associate with product")
    is_public: bool = Field(default=False, description="Whether file should be publicly accessible")
    resize_image: bool = Field(default=True, description="Whether to resize images")
    generate_thumbnails: bool = Field(default=True, description="Whether to generate thumbnails")


class FileUploadResponse(BaseSchema):
    """Response schema for file upload."""
    
    file: FileResponse
    thumbnails: Optional[List["ThumbnailResponse"]] = None
    processing_status: str = Field(default="completed", description="File processing status")
    warnings: Optional[List[str]] = None


class MultipleFileUploadRequest(BaseSchema):
    """Request schema for multiple file upload."""
    
    files: List[FileUploadRequest]
    collection_id: Optional[UUID] = Field(None, description="Default collection for all files")
    product_id: Optional[UUID] = Field(None, description="Default product for all files")


class MultipleFileUploadResponse(BaseSchema):
    """Response schema for multiple file upload."""
    
    uploaded_files: List[FileUploadResponse]
    failed_uploads: List[Dict[str, Any]] = Field(default_factory=list, description="Failed upload details")
    total_uploaded: int
    total_failed: int


# Image Processing Schemas

class ImageDimensions(BaseSchema):
    """Image dimensions schema."""
    
    width: int = Field(gt=0, description="Width in pixels")
    height: int = Field(gt=0, description="Height in pixels")
    aspect_ratio: float = Field(description="Aspect ratio (width/height)")


class ImageMetadata(BaseSchema):
    """Enhanced image metadata schema."""
    
    dimensions: ImageDimensions
    format: str = Field(description="Image format (JPEG, PNG, WebP, etc.)")
    mode: Optional[str] = Field(None, description="Color mode (RGB, RGBA, etc.)")
    has_transparency: bool = Field(default=False, description="Whether image has transparency")
    color_profile: Optional[str] = Field(None, description="Color profile information")
    dpi: Optional[Dict[str, int]] = Field(None, description="DPI information")
    exif_data: Optional[Dict[str, Any]] = Field(None, description="EXIF metadata")


class ThumbnailResponse(BaseSchema):
    """Thumbnail information schema."""
    
    size: str = Field(description="Thumbnail size designation (e.g., 'small', 'medium', 'large')")
    dimensions: ImageDimensions
    url: str = Field(description="Thumbnail URL")
    file_size: int = Field(description="Thumbnail file size in bytes")


class ImageProcessingRequest(BaseSchema):
    """Request schema for image processing."""
    
    resize_to: Optional[ImageDimensions] = Field(None, description="Resize to specific dimensions")
    max_width: Optional[int] = Field(None, gt=0, le=4000, description="Maximum width")
    max_height: Optional[int] = Field(None, gt=0, le=4000, description="Maximum height")
    quality: Optional[int] = Field(None, ge=1, le=100, description="Image quality (1-100)")
    format: Optional[str] = Field(None, description="Target format (JPEG, PNG, WebP)")
    preserve_exif: bool = Field(default=False, description="Whether to preserve EXIF data")
    create_thumbnails: bool = Field(default=True, description="Whether to create thumbnails")
    thumbnail_sizes: Optional[List[str]] = Field(
        default=["small", "medium", "large"],
        description="Thumbnail sizes to generate"
    )


class ImageProcessingResponse(BaseSchema):
    """Response schema for image processing."""
    
    original_file: FileResponse
    processed_file: Optional[FileResponse] = None
    thumbnails: List[ThumbnailResponse] = Field(default_factory=list)
    processing_time: float = Field(description="Processing time in seconds")
    operations_performed: List[str] = Field(description="List of operations performed")


# Document Processing Schemas

class DocumentMetadata(BaseSchema):
    """Document metadata schema."""
    
    page_count: Optional[int] = Field(None, description="Number of pages")
    author: Optional[str] = Field(None, description="Document author")
    title: Optional[str] = Field(None, description="Document title")
    subject: Optional[str] = Field(None, description="Document subject")
    keywords: Optional[List[str]] = Field(None, description="Document keywords")
    created_date: Optional[str] = Field(None, description="Document creation date")
    modified_date: Optional[str] = Field(None, description="Document modification date")
    application: Optional[str] = Field(None, description="Creating application")
    security: Optional[Dict[str, Any]] = Field(None, description="Security settings")


class DocumentProcessingRequest(BaseSchema):
    """Request schema for document processing."""
    
    extract_text: bool = Field(default=True, description="Whether to extract text content")
    extract_metadata: bool = Field(default=True, description="Whether to extract metadata")
    create_preview: bool = Field(default=True, description="Whether to create preview images")
    ocr_language: Optional[str] = Field(None, description="OCR language code")


class DocumentProcessingResponse(BaseSchema):
    """Response schema for document processing."""
    
    original_file: FileResponse
    extracted_text: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None
    preview_images: Optional[List[str]] = None
    processing_time: float = Field(description="Processing time in seconds")


# File Management Schemas

class FileListFilters(BaseSchema):
    """Filters for file listing."""
    
    content_type: Optional[str] = Field(None, description="Filter by content type")
    file_type: Optional[str] = Field(None, description="Filter by file type (image, document, etc.)")
    collection_id: Optional[UUID] = Field(None, description="Filter by collection")
    product_id: Optional[UUID] = Field(None, description="Filter by product")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    min_size: Optional[int] = Field(None, ge=0, description="Minimum file size")
    max_size: Optional[int] = Field(None, ge=0, description="Maximum file size")
    query: Optional[str] = Field(None, description="Search query for filename/description")
    date_from: Optional[str] = Field(None, description="Filter files created after this date")
    date_to: Optional[str] = Field(None, description="Filter files created before this date")


class FileBatchOperation(BaseSchema):
    """Schema for batch file operations."""
    
    file_ids: List[UUID] = Field(..., min_length=1, description="List of file IDs")
    operation: str = Field(..., description="Operation to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Operation parameters")
    
    @field_validator('operation')
    @classmethod
    def validate_operation(cls, v: str) -> str:
        """Validate batch operation."""
        valid_operations = ["delete", "move", "copy", "tag", "untag", "update_metadata"]
        if v not in valid_operations:
            raise ValueError(f"Operation must be one of: {', '.join(valid_operations)}")
        return v


class FileBatchOperationResponse(BaseSchema):
    """Response schema for batch file operations."""
    
    successful_operations: int
    failed_operations: int
    total_operations: int
    results: List[Dict[str, Any]] = Field(description="Detailed results for each operation")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Errors encountered")


class FileAnalytics(BaseSchema):
    """File analytics schema."""
    
    total_files: int
    total_size: int
    files_by_type: Dict[str, int]
    files_by_month: Dict[str, int]
    average_file_size: float
    most_downloaded: List[Dict[str, Any]]
    storage_usage: Dict[str, Union[int, str]]


class FileStorageInfo(BaseSchema):
    """File storage information schema."""
    
    storage_provider: str = Field(description="Storage provider name")
    bucket_name: str = Field(description="Storage bucket/container name")
    region: Optional[str] = Field(None, description="Storage region")
    cdn_enabled: bool = Field(description="Whether CDN is enabled")
    cdn_url: Optional[str] = Field(None, description="CDN base URL")
    backup_enabled: bool = Field(description="Whether backup is enabled")
    encryption_enabled: bool = Field(description="Whether encryption is enabled")


# Forward references
from .collection import CollectionSummary
from .product import ProductSummaryResponse

FileResponse.model_rebuild()
