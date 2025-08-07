"""
File Repository

Data access layer for File entity.
Handles file metadata and storage references.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.repositories.base import BaseRepository


class FileRepository(BaseRepository[File]):
    """
    File repository for managing uploaded files and their metadata.
    """

    def __init__(self, db: AsyncSession):
        """Initialize with File model."""
        super().__init__(db, File)

    async def get_by_filename(self, filename: str) -> Optional[File]:
        """
        Get file by filename.
        
        Args:
            filename: File name
            
        Returns:
            File or None if not found
        """
        return await self.get_by_field("filename", filename)

    async def get_by_hash(self, hash_value: str, hash_type: str = "md5") -> Optional[File]:
        """
        Get file by hash value.
        
        Args:
            hash_value: Hash value
            hash_type: Hash type (md5 or sha256)
            
        Returns:
            File or None if not found
        """
        field_name = f"hash_{hash_type}"
        return await self.get_by_field(field_name, hash_value)

    async def get_files_by_collection(
        self,
        collection_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[File]:
        """
        Get files associated with a collection.
        
        Args:
            collection_id: Collection UUID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of files for the collection
        """
        query = (
            select(File)
            .where(and_(
                File.collection_id == collection_id,
                File.is_deleted == False
            ))
            .order_by(File.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_files_by_product(
        self,
        product_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[File]:
        """
        Get files associated with a product.
        
        Args:
            product_id: Product UUID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of files for the product
        """
        query = (
            select(File)
            .where(and_(
                File.product_id == product_id,
                File.is_deleted == False
            ))
            .order_by(File.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_files_by_content_type(
        self,
        content_type: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[File]:
        """
        Get files by content type.
        
        Args:
            content_type: MIME content type
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of files with matching content type
        """
        query = (
            select(File)
            .where(and_(
                File.content_type.startswith(content_type),
                File.is_deleted == False
            ))
            .order_by(File.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def search_files(
        self,
        search_term: str,
        content_type_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[File]:
        """
        Search files by filename or description.
        
        Args:
            search_term: Text to search for
            content_type_filter: Optional content type filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of matching files
        """
        search_pattern = f"%{search_term}%"
        
        query = (
            select(File)
            .where(and_(
                File.is_deleted == False,
                or_(
                    File.filename.ilike(search_pattern),
                    File.original_filename.ilike(search_pattern),
                    File.description.ilike(search_pattern)
                )
            ))
        )
        
        if content_type_filter:
            query = query.where(File.content_type.startswith(content_type_filter))
        
        query = query.order_by(File.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_files_with_filters(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 50
    ) -> List[File]:
        """
        Get files with advanced filtering.
        
        Args:
            filters: Dictionary of filters to apply
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of filtered files
        """
        query = select(File).where(File.is_deleted == False)
        
        # Apply filters
        if filters.get('content_type'):
            query = query.where(File.content_type.startswith(filters['content_type']))
        
        if filters.get('collection_id'):
            query = query.where(File.collection_id == filters['collection_id'])
        
        if filters.get('product_id'):
            query = query.where(File.product_id == filters['product_id'])
        
        if filters.get('min_size'):
            query = query.where(File.size >= filters['min_size'])
        
        if filters.get('max_size'):
            query = query.where(File.size <= filters['max_size'])
        
        if filters.get('query'):
            search_pattern = f"%{filters['query']}%"
            query = query.where(or_(
                File.filename.ilike(search_pattern),
                File.description.ilike(search_pattern)
            ))
        
        if filters.get('tags'):
            # Assuming tags are stored as JSON array
            for tag in filters['tags']:
                query = query.where(File.tags.contains([tag]))
        
        if filters.get('date_from'):
            query = query.where(File.created_at >= filters['date_from'])
        
        if filters.get('date_to'):
            query = query.where(File.created_at <= filters['date_to'])
        
        query = query.order_by(File.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_storage_statistics(self) -> Dict[str, Any]:
        """
        Get storage usage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        # Total files and size
        total_query = select(
            func.count(File.id),
            func.sum(File.size)
        ).where(File.is_deleted == False)
        
        total_result = await self.db.execute(total_query)
        total_row = total_result.fetchone()
        total_files = total_row[0] or 0
        total_size = total_row[1] or 0
        
        # Files by content type
        type_query = (
            select(
                func.substr(File.content_type, 1, func.position('/' in File.content_type) - 1).label('type'),
                func.count(File.id).label('count'),
                func.sum(File.size).label('size')
            )
            .where(File.is_deleted == False)
            .group_by('type')
        )
        
        type_result = await self.db.execute(type_query)
        files_by_type = {}
        for row in type_result:
            files_by_type[row[0]] = {
                'count': row[1],
                'size': row[2]
            }
        
        # Average file size
        avg_size = total_size / total_files if total_files > 0 else 0
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'average_file_size': avg_size,
            'files_by_type': files_by_type
        }

    async def get_largest_files(self, limit: int = 10) -> List[File]:
        """
        Get the largest files by size.
        
        Args:
            limit: Number of files to return
            
        Returns:
            List of largest files
        """
        query = (
            select(File)
            .where(File.is_deleted == False)
            .order_by(desc(File.size))
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_orphaned_files(self) -> List[File]:
        """
        Get files that are not associated with any collection or product.
        
        Returns:
            List of orphaned files
        """
        query = (
            select(File)
            .where(and_(
                File.is_deleted == False,
                File.collection_id.is_(None),
                File.product_id.is_(None)
            ))
            .order_by(File.created_at.desc())
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_download_count(self, file_id: UUID) -> bool:
        """
        Increment download count for a file.
        
        Args:
            file_id: File UUID
            
        Returns:
            True if updated successfully
        """
        from sqlalchemy import update
        from datetime import datetime
        
        query = (
            update(File)
            .where(and_(File.id == file_id, File.is_deleted == False))
            .values(
                download_count=File.download_count + 1,
                last_accessed=datetime.utcnow()
            )
        )
        
        result = await self.db.execute(query)
        return result.rowcount > 0

    async def cleanup_deleted_files(self, days_old: int = 30) -> List[File]:
        """
        Get files that have been soft-deleted for more than specified days.
        
        Args:
            days_old: Number of days since deletion
            
        Returns:
            List of files ready for permanent deletion
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        query = (
            select(File)
            .where(and_(
                File.is_deleted == True,
                File.deleted_at <= cutoff_date
            ))
            .order_by(File.deleted_at)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
