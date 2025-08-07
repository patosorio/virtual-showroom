"""
File Management API Routes

REST API endpoints for file upload, management, and processing.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File as FastAPIFile, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.file import FileService
from app.schemas.file import (
    FileResponse, FileUploadRequest, FileUploadResponse,
    MultipleFileUploadResponse, FileListFilters,
    FileBatchOperation, FileBatchOperationResponse,
    ImageProcessingRequest, ImageProcessingResponse,
    DocumentProcessingRequest, DocumentProcessingResponse,
    FileAnalytics
)
from app.schemas.base import PaginatedResponse
from fastapi import HTTPException

router = APIRouter()


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file",
    description="Upload a single file"
)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    description: Optional[str] = Form(None),
    collection_id: Optional[UUID] = Form(None),
    product_id: Optional[UUID] = Form(None),
    is_public: bool = Form(False),
    resize_image: bool = Form(True),
    generate_thumbnails: bool = Form(True),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload a file."""
    try:
        service = FileService(db)
        
        upload_request = FileUploadRequest(
            description=description,
            tags=[],
            collection_id=collection_id,
            product_id=product_id,
            is_public=is_public,
            resize_image=resize_image,
            generate_thumbnails=generate_thumbnails
        )
        
        result = await service.upload_file(
            file_content=file.file,
            original_filename=file.filename,
            upload_request=upload_request,
            user_id=UUID(current_user["uid"])
        )
        
        return result
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while uploading the file"
        )


@router.get(
    "/",
    response_model=PaginatedResponse[FileResponse],
    summary="List files",
    description="Get a paginated list of files with optional filtering"
)
async def list_files(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of items to return"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    collection_id: Optional[UUID] = Query(None, description="Filter by collection"),
    product_id: Optional[UUID] = Query(None, description="Filter by product"),
    min_size: Optional[int] = Query(None, ge=0, description="Minimum file size"),
    max_size: Optional[int] = Query(None, ge=0, description="Maximum file size"),
    query: Optional[str] = Query(None, description="Search query"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """List files with pagination and filtering."""
    try:
        service = FileService(db)
        
        # Build filters
        filters = FileListFilters(
            content_type=content_type,
            collection_id=collection_id,
            product_id=product_id,
            min_size=min_size,
            max_size=max_size,
            query=query
        )
        
        # Get files
        files, total = await service.list_files(
            filters=filters,
            skip=skip,
            limit=limit,
            user_id=UUID(current_user["uid"]) if current_user else None
        )
        
        # Convert to response models
        file_responses = [
            FileResponse.model_validate(file)
            for file in files
        ]
        
        return PaginatedResponse.create(
            items=file_responses,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while listing files"
        )


@router.get(
    "/{file_id}",
    response_model=FileResponse,
    summary="Get file by ID",
    description="Get file metadata by ID"
)
async def get_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get file by ID."""
    try:
        service = FileService(db)
        
        file = await service.get_file_with_download_tracking(file_id)
        
        return FileResponse.model_validate(file)
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the file"
        )


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete file",
    description="Delete a file (admin only)"
)
async def delete_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a file."""
    try:
        service = FileService(db)
        
        await service.delete(
            id=file_id,
            user_id=UUID(current_user["uid"])
        )
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the file"
        )


@router.get(
    "/search/",
    response_model=List[FileResponse],
    summary="Search files",
    description="Search files by filename or description"
)
async def search_files(
    q: str = Query(..., min_length=2, description="Search query"),
    content_type_filter: Optional[str] = Query(None, description="Filter by content type"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of items to return"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Search files."""
    try:
        service = FileService(db)
        
        files = await service.search_files(
            query=q,
            content_type_filter=content_type_filter,
            skip=skip,
            limit=limit
        )
        
        return [FileResponse.model_validate(file) for file in files]
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while searching files"
        )


@router.post(
    "/{file_id}/process/image",
    response_model=ImageProcessingResponse,
    summary="Process image",
    description="Process an image file (resize, optimize, thumbnails)"
)
async def process_image(
    file_id: UUID,
    processing_request: ImageProcessingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Process an image file."""
    try:
        service = FileService(db)
        
        result = await service.process_image(
            file_id=file_id,
            processing_request=processing_request,
            user_id=UUID(current_user["uid"])
        )
        
        return result
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the image"
        )


@router.post(
    "/{file_id}/process/document",
    response_model=DocumentProcessingResponse,
    summary="Process document",
    description="Process a document file (extract text, metadata, previews)"
)
async def process_document(
    file_id: UUID,
    processing_request: DocumentProcessingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Process a document file."""
    try:
        service = FileService(db)
        
        result = await service.process_document(
            file_id=file_id,
            processing_request=processing_request,
            user_id=UUID(current_user["uid"])
        )
        
        return result
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the document"
        )


@router.post(
    "/batch",
    response_model=FileBatchOperationResponse,
    summary="Batch file operations",
    description="Perform batch operations on multiple files (admin only)"
)
async def batch_file_operations(
    operation: FileBatchOperation,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Perform batch operations on files."""
    try:
        service = FileService(db)
        
        result = await service.batch_operation(
            operation=operation,
            user_id=UUID(current_user["uid"])
        )
        
        return result
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during batch operation"
        )


@router.get(
    "/analytics/",
    response_model=FileAnalytics,
    summary="Get file analytics",
    description="Get file storage analytics (admin only)"
)
async def get_file_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get file analytics."""
    try:
        service = FileService(db)
        
        analytics = await service.get_file_analytics()
        
        return analytics
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving analytics"
        )
