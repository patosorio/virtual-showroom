"""
File Service

Business logic for File entity.
Handles file upload, processing, and management operations.
"""

import os
import hashlib
import mimetypes
from typing import List, Optional, Dict, Any, Tuple, BinaryIO
from uuid import UUID
from pathlib import Path
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.repositories.file import FileRepository
from app.services.base import BaseService
from app.core.exceptions import ValidationError, NotFoundError, BadRequestError
from app.schemas.file import (
    FileCreate, FileUpdate, FileResponse,
    FileUploadRequest, FileUploadResponse,
    MultipleFileUploadRequest, MultipleFileUploadResponse,
    FileListFilters, FileBatchOperation, FileBatchOperationResponse,
    ImageProcessingRequest, ImageProcessingResponse,
    DocumentProcessingRequest, DocumentProcessingResponse,
    FileAnalytics
)


class FileService(BaseService[File, FileRepository]):
    """
    File service with business logic for file management.
    """

    def __init__(self, db: AsyncSession):
        """Initialize file service."""
        super().__init__(db, FileRepository, File)
        
        # File storage configuration
        self.storage_path = os.getenv("FILE_STORAGE_PATH", "/tmp/uploads")
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "104857600"))  # 100MB default
        self.allowed_image_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
        self.allowed_document_types = {"application/pdf", "application/msword", 
                                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
        
        # Ensure storage directory exists
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        file_content: BinaryIO,
        original_filename: str,
        upload_request: FileUploadRequest,
        user_id: Optional[UUID] = None
    ) -> FileUploadResponse:
        """
        Upload and process a single file.
        
        Args:
            file_content: File content stream
            original_filename: Original filename
            upload_request: Upload configuration
            user_id: ID of uploading user
            
        Returns:
            File upload response with metadata
        """
        # Read file content
        content = file_content.read()
        file_size = len(content)
        
        # Validate file
        await self._validate_file_upload(content, original_filename, file_size)
        
        # Detect content type
        content_type, _ = mimetypes.guess_type(original_filename)
        if not content_type:
            content_type = "application/octet-stream"
        
        # Generate unique filename
        file_extension = Path(original_filename).suffix.lower()
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{original_filename}"
        
        # Calculate file hashes
        md5_hash = hashlib.md5(content).hexdigest()
        sha256_hash = hashlib.sha256(content).hexdigest()
        
        # Check for duplicate files
        existing_file = await self.repository.get_by_hash(md5_hash, "md5")
        if existing_file:
            # Return existing file instead of uploading duplicate
            return FileUploadResponse(
                file=FileResponse.model_validate(existing_file),
                processing_status="completed",
                warnings=["File already exists, returning existing file"]
            )
        
        # Save file to storage
        storage_path = await self._save_file_to_storage(content, unique_filename)
        
        # Create file record
        file_data = FileCreate(
            filename=unique_filename,
            original_filename=original_filename,
            content_type=content_type,
            size=file_size,
            url=f"/files/{unique_filename}",  # This would be the actual URL
            storage_path=storage_path,
            hash_md5=md5_hash,
            hash_sha256=sha256_hash,
            description=upload_request.description,
            tags=upload_request.tags or [],
            collection_id=upload_request.collection_id,
            product_id=upload_request.product_id,
            metadata=await self._extract_file_metadata(content, content_type)
        )
        
        # Create file record in database
        file_record = await self.repository.create(file_data.model_dump(), user_id)
        
        # Process file if needed
        processing_status = "completed"
        thumbnails = []
        warnings = []
        
        if content_type.startswith("image/") and upload_request.generate_thumbnails:
            try:
                thumbnails = await self._generate_image_thumbnails(file_record, content)
            except Exception as e:
                warnings.append(f"Failed to generate thumbnails: {str(e)}")
        
        return FileUploadResponse(
            file=FileResponse.model_validate(file_record),
            thumbnails=thumbnails,
            processing_status=processing_status,
            warnings=warnings if warnings else None
        )

    async def upload_multiple_files(
        self,
        files_data: List[Tuple[BinaryIO, str]],  # (content, filename) pairs
        upload_request: MultipleFileUploadRequest,
        user_id: Optional[UUID] = None
    ) -> MultipleFileUploadResponse:
        """
        Upload multiple files in batch.
        
        Args:
            files_data: List of (file_content, filename) tuples
            upload_request: Upload configuration for all files
            user_id: ID of uploading user
            
        Returns:
            Multiple file upload response
        """
        uploaded_files = []
        failed_uploads = []
        
        for i, (file_content, original_filename) in enumerate(files_data):
            try:
                # Create individual upload request
                individual_request = FileUploadRequest(
                    description=upload_request.files[i].description if i < len(upload_request.files) else None,
                    tags=upload_request.files[i].tags if i < len(upload_request.files) else [],
                    collection_id=upload_request.collection_id,
                    product_id=upload_request.product_id,
                    is_public=upload_request.files[i].is_public if i < len(upload_request.files) else False,
                    resize_image=upload_request.files[i].resize_image if i < len(upload_request.files) else True,
                    generate_thumbnails=upload_request.files[i].generate_thumbnails if i < len(upload_request.files) else True
                )
                
                # Upload individual file
                upload_result = await self.upload_file(
                    file_content, original_filename, individual_request, user_id
                )
                uploaded_files.append(upload_result)
                
            except Exception as e:
                failed_uploads.append({
                    "filename": original_filename,
                    "error": str(e),
                    "index": i
                })
        
        return MultipleFileUploadResponse(
            uploaded_files=uploaded_files,
            failed_uploads=failed_uploads,
            total_uploaded=len(uploaded_files),
            total_failed=len(failed_uploads)
        )

    async def get_file_with_download_tracking(self, file_id: UUID) -> File:
        """
        Get file and track download.
        
        Args:
            file_id: File UUID
            
        Returns:
            File record
        """
        file_record = await self.repository.get_by_id(file_id)
        if not file_record:
            raise NotFoundError(
                detail=f"File with ID {file_id} not found",
                error_code="FILE_NOT_FOUND"
            )
        
        # Update download count
        await self.repository.update_download_count(file_id)
        
        return file_record

    async def list_files(
        self,
        filters: FileListFilters,
        skip: int = 0,
        limit: int = 50,
        user_id: Optional[UUID] = None
    ) -> Tuple[List[File], int]:
        """
        List files with filtering and pagination.
        
        Args:
            filters: Filter parameters
            skip: Number of records to skip
            limit: Maximum records to return
            user_id: ID of requesting user
            
        Returns:
            Tuple of (files, total_count)
        """
        # Convert filters to dict
        filter_dict = filters.model_dump(exclude_unset=True)
        
        # Apply business logic filters
        business_filters = await self._apply_business_filters(filter_dict, user_id)
        
        # Get files from repository
        files = await self.repository.get_files_with_filters(
            business_filters, skip, limit
        )
        
        # Get total count
        total = await self.repository.count(filters=business_filters)
        
        return files, total

    async def search_files(
        self,
        query: str,
        content_type_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[File]:
        """
        Search files by filename or description.
        
        Args:
            query: Search query
            content_type_filter: Optional content type filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of matching files
        """
        if not query or len(query.strip()) < 2:
            raise ValidationError(
                detail="Search query must be at least 2 characters long",
                error_code="INVALID_SEARCH_QUERY"
            )
        
        return await self.repository.search_files(
            query.strip(), content_type_filter, skip, limit
        )

    async def process_image(
        self,
        file_id: UUID,
        processing_request: ImageProcessingRequest,
        user_id: Optional[UUID] = None
    ) -> ImageProcessingResponse:
        """
        Process an image file (resize, optimize, generate thumbnails).
        
        Args:
            file_id: File UUID
            processing_request: Processing configuration
            user_id: ID of user requesting processing
            
        Returns:
            Image processing response
        """
        file_record = await self.repository.get_by_id(file_id)
        if not file_record:
            raise NotFoundError(
                detail=f"File with ID {file_id} not found",
                error_code="FILE_NOT_FOUND"
            )
        
        if not file_record.content_type.startswith("image/"):
            raise ValidationError(
                detail="File is not an image",
                error_code="NOT_AN_IMAGE"
            )
        
        # This would contain actual image processing logic
        # For now, return a placeholder response
        return ImageProcessingResponse(
            original_file=FileResponse.model_validate(file_record),
            processing_time=0.5,
            operations_performed=["validation"]
        )

    async def process_document(
        self,
        file_id: UUID,
        processing_request: DocumentProcessingRequest,
        user_id: Optional[UUID] = None
    ) -> DocumentProcessingResponse:
        """
        Process a document file (extract text, metadata, create previews).
        
        Args:
            file_id: File UUID
            processing_request: Processing configuration
            user_id: ID of user requesting processing
            
        Returns:
            Document processing response
        """
        file_record = await self.repository.get_by_id(file_id)
        if not file_record:
            raise NotFoundError(
                detail=f"File with ID {file_id} not found",
                error_code="FILE_NOT_FOUND"
            )
        
        if file_record.content_type not in self.allowed_document_types:
            raise ValidationError(
                detail="File is not a supported document type",
                error_code="UNSUPPORTED_DOCUMENT_TYPE"
            )
        
        # This would contain actual document processing logic
        # For now, return a placeholder response
        return DocumentProcessingResponse(
            original_file=FileResponse.model_validate(file_record),
            processing_time=1.0
        )

    async def batch_operation(
        self,
        operation: FileBatchOperation,
        user_id: Optional[UUID] = None
    ) -> FileBatchOperationResponse:
        """
        Perform batch operations on multiple files.
        
        Args:
            operation: Batch operation configuration
            user_id: ID of user performing operation
            
        Returns:
            Batch operation response
        """
        successful_operations = 0
        failed_operations = 0
        results = []
        errors = []
        
        for file_id in operation.file_ids:
            try:
                if operation.operation == "delete":
                    success = await self.repository.delete(file_id, user_id, soft=True)
                    if success:
                        successful_operations += 1
                        results.append({"file_id": str(file_id), "status": "deleted"})
                    else:
                        failed_operations += 1
                        errors.append({"file_id": str(file_id), "error": "File not found"})
                
                elif operation.operation == "tag":
                    # Add tags to file
                    tags = operation.parameters.get("tags", [])
                    file_record = await self.repository.get_by_id(file_id)
                    if file_record:
                        existing_tags = file_record.tags or []
                        new_tags = list(set(existing_tags + tags))
                        await self.repository.update(file_id, {"tags": new_tags}, user_id)
                        successful_operations += 1
                        results.append({"file_id": str(file_id), "status": "tagged"})
                    else:
                        failed_operations += 1
                        errors.append({"file_id": str(file_id), "error": "File not found"})
                
                # Add other operations as needed
                
            except Exception as e:
                failed_operations += 1
                errors.append({"file_id": str(file_id), "error": str(e)})
        
        return FileBatchOperationResponse(
            successful_operations=successful_operations,
            failed_operations=failed_operations,
            total_operations=len(operation.file_ids),
            results=results,
            errors=errors
        )

    async def get_file_analytics(self) -> FileAnalytics:
        """
        Get file storage analytics.
        
        Returns:
            File analytics data
        """
        stats = await self.repository.get_storage_statistics()
        largest_files = await self.repository.get_largest_files(10)
        
        # Calculate additional metrics
        storage_usage = {
            "total_bytes": stats.get("total_size", 0),
            "total_human": self._format_file_size(stats.get("total_size", 0)),
            "average_file_size": stats.get("average_file_size", 0)
        }
        
        # Get files by month (simplified)
        files_by_month = {}  # This would be calculated from creation dates
        
        # Get most downloaded files (simplified)
        most_downloaded = []  # This would query files ordered by download_count
        
        return FileAnalytics(
            total_files=stats.get("total_files", 0),
            total_size=stats.get("total_size", 0),
            files_by_type=stats.get("files_by_type", {}),
            files_by_month=files_by_month,
            average_file_size=stats.get("average_file_size", 0),
            most_downloaded=most_downloaded,
            storage_usage=storage_usage
        )

    async def cleanup_orphaned_files(self) -> int:
        """
        Clean up files that are not associated with any entity.
        
        Returns:
            Number of files cleaned up
        """
        orphaned_files = await self.repository.get_orphaned_files()
        
        # Move orphaned files to deleted status
        deleted_count = 0
        for file_record in orphaned_files:
            try:
                await self.repository.delete(file_record.id, soft=True)
                deleted_count += 1
            except Exception:
                pass  # Continue with other files
        
        return deleted_count

    # Helper Methods

    async def _validate_file_upload(
        self,
        content: bytes,
        filename: str,
        file_size: int
    ) -> None:
        """Validate file upload constraints."""
        # Check file size
        if file_size > self.max_file_size:
            raise ValidationError(
                detail=f"File size exceeds maximum allowed size of {self._format_file_size(self.max_file_size)}",
                error_code="FILE_TOO_LARGE"
            )
        
        # Check file extension
        file_extension = Path(filename).suffix.lower()
        if not file_extension:
            raise ValidationError(
                detail="File must have an extension",
                error_code="NO_FILE_EXTENSION"
            )
        
        # Detect content type
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = "application/octet-stream"
        
        # Validate content type for images
        if content_type.startswith("image/"):
            if content_type not in self.allowed_image_types:
                raise ValidationError(
                    detail=f"Image type {content_type} is not allowed",
                    error_code="INVALID_IMAGE_TYPE"
                )
        
        # Basic security check - scan for malicious content
        await self._scan_file_content(content, content_type)

    async def _scan_file_content(self, content: bytes, content_type: str) -> None:
        """Basic security scan of file content."""
        # Check for executable file signatures
        dangerous_signatures = [
            b'\x4D\x5A',  # Windows PE executable
            b'\x7F\x45\x4C\x46',  # Linux ELF executable
            b'\xCA\xFE\xBA\xBE',  # Java class file
        ]
        
        for signature in dangerous_signatures:
            if content.startswith(signature):
                raise ValidationError(
                    detail="Executable files are not allowed",
                    error_code="EXECUTABLE_FILE_DETECTED"
                )

    async def _save_file_to_storage(self, content: bytes, filename: str) -> str:
        """Save file content to storage and return path."""
        # Create subdirectory based on date
        date_dir = datetime.utcnow().strftime("%Y/%m/%d")
        full_dir = Path(self.storage_path) / date_dir
        full_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = full_dir / filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        return str(file_path)

    async def _extract_file_metadata(
        self,
        content: bytes,
        content_type: str
    ) -> Dict[str, Any]:
        """Extract metadata from file content."""
        metadata = {
            "content_length": len(content),
            "content_type": content_type
        }
        
        # Extract image metadata if it's an image
        if content_type.startswith("image/"):
            try:
                # This would use PIL or similar to extract image metadata
                # For now, just add basic info
                metadata["file_type"] = "image"
                metadata["format"] = content_type.split("/")[1].upper()
            except Exception:
                pass
        
        return metadata

    async def _generate_image_thumbnails(
        self,
        file_record: File,
        content: bytes
    ) -> List[Dict[str, Any]]:
        """Generate thumbnails for image files."""
        # This would use PIL or similar for actual thumbnail generation
        # For now, return placeholder data
        return [
            {
                "size": "small",
                "width": 150,
                "height": 150,
                "url": f"/thumbnails/{file_record.filename}_small.jpg"
            },
            {
                "size": "medium", 
                "width": 300,
                "height": 300,
                "url": f"/thumbnails/{file_record.filename}_medium.jpg"
            }
        ]

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

    async def _apply_business_filters(
        self,
        filters: Optional[Dict[str, Any]],
        user_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Apply business logic filters."""
        if not filters:
            filters = {}
        
        # Non-admin users might have restricted access
        # For now, no additional filters
        
        return filters
