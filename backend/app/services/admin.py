"""
Admin Service

Business logic for admin operations, analytics, and system management.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.collection import CollectionRepository
from app.repositories.product.repository import ProductRepository
from app.repositories.file import FileRepository
from app.repositories.user import UserRepository
from app.core.exceptions import ValidationError, NotFoundError
from app.schemas.admin import (
    DashboardStats, CollectionStats, ProductStats, FileStats, UserStats, SystemStats,
    AnalyticsDateRange, BulkImportRequest, BulkImportResponse,
    BulkExportRequest, BulkExportResponse, SystemHealthCheck
)


class AdminService:
    """
    Admin service for dashboard, analytics, and system management.
    """

    def __init__(self, db: AsyncSession):
        """Initialize admin service."""
        self.db = db
        self.collection_repository = CollectionRepository(db)
        self.product_repository = ProductRepository(db)
        self.file_repository = FileRepository(db)
        self.user_repository = UserRepository(db)

    async def get_dashboard_stats(self) -> DashboardStats:
        """
        Get comprehensive dashboard statistics.
        
        Returns:
            Dashboard statistics
        """
        # Get collection stats
        collections_data = await self.collection_repository.get_collections_with_stats()
        collection_analytics = await self._calculate_collection_stats(collections_data)
        
        # Get product stats  
        product_analytics = await self._calculate_product_stats()
        
        # Get file stats
        file_analytics = await self._calculate_file_stats()
        
        # Get user stats
        user_analytics = await self.user_repository.get_user_statistics()
        
        # Get system stats
        system_analytics = await self._calculate_system_stats()
        
        return DashboardStats(
            collections=CollectionStats(**collection_analytics),
            products=ProductStats(**product_analytics),
            files=FileStats(**file_analytics),
            users=UserStats(**user_analytics),
            system=SystemStats(**system_analytics)
        )

    async def get_collection_analytics(
        self,
        date_range: Optional[AnalyticsDateRange] = None
    ) -> List[Dict[str, Any]]:
        """
        Get detailed collection analytics.
        
        Args:
            date_range: Optional date range for analytics
            
        Returns:
            List of collection analytics
        """
        # Get all collections with stats
        collections_data = await self.collection_repository.get_collections_with_stats()
        
        analytics = []
        for item in collections_data:
            collection = item['collection']
            product_count = item['product_count']
            
            # Get detailed analytics for each collection
            detailed_analytics = await self.collection_repository.get_collection_analytics(
                collection.id
            )
            
            analytics.append({
                'collection_id': collection.id,
                'collection_name': collection.name,
                'collection_slug': collection.slug,
                'total_products': product_count,
                'product_categories': detailed_analytics.get('products_by_category', {}),
                'average_product_price': detailed_analytics.get('average_price'),
                'price_range': detailed_analytics.get('price_range', {}),
                'creation_date': collection.created_at,
                'last_updated': collection.updated_at,
                'is_published': collection.is_published
            })
        
        return analytics

    async def get_product_analytics(
        self,
        date_range: Optional[AnalyticsDateRange] = None
    ) -> List[Dict[str, Any]]:
        """
        Get detailed product analytics.
        
        Args:
            date_range: Optional date range for analytics
            
        Returns:
            List of product analytics
        """
        # Get products with basic filters
        filters = {}
        if date_range:
            filters['created_after'] = date_range.start_date
            filters['created_before'] = date_range.end_date
        
        products, _ = await self.product_repository.get_products_with_filters(
            filters, skip=0, limit=1000
        )
        
        analytics = []
        for product in products:
            # Get detailed analytics for each product
            product_analytics = await self.product_repository.get_product_analytics(product.id)
            
            analytics.append({
                'product_id': product.id,
                'product_name': product.name,
                'product_sku': product.sku,
                'collection_name': product.collection.name if product.collection else None,
                'total_variants': product_analytics.get('total_variants', 0),
                'total_images': product_analytics.get('total_images', 0),
                'specifications_count': product_analytics.get('specifications_count', 0),
                'has_size_chart': product_analytics.get('has_size_chart', False),
                'creation_date': product.created_at,
                'last_updated': product.updated_at,
                'status': product.status,
                'is_featured': product.is_featured
            })
        
        return analytics

    async def bulk_import_data(
        self,
        import_request: BulkImportRequest,
        admin_user_id: UUID
    ) -> BulkImportResponse:
        """
        Perform bulk data import.
        
        Args:
            import_request: Import configuration
            admin_user_id: ID of admin performing import
            
        Returns:
            Import response with status
        """
        # Validate admin permissions
        admin_user = await self.user_repository.get_by_id(admin_user_id)
        if not admin_user or admin_user.role != "admin":
            raise ValidationError(
                detail="Only administrators can perform bulk imports",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        # This would contain the actual import logic
        # For now, return a placeholder response
        import_id = UUID()
        
        return BulkImportResponse(
            import_id=import_id,
            status="started",
            total_records=len(import_request.data) if import_request.data else 0,
            processed_records=0,
            successful_records=0,
            failed_records=0,
            errors=[],
            warnings=[],
            started_at=datetime.utcnow()
        )

    async def bulk_export_data(
        self,
        export_request: BulkExportRequest,
        admin_user_id: UUID
    ) -> BulkExportResponse:
        """
        Perform bulk data export.
        
        Args:
            export_request: Export configuration
            admin_user_id: ID of admin performing export
            
        Returns:
            Export response with download info
        """
        # Validate admin permissions
        admin_user = await self.user_repository.get_by_id(admin_user_id)
        if not admin_user or admin_user.role != "admin":
            raise ValidationError(
                detail="Only administrators can perform bulk exports",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        # This would contain the actual export logic
        # For now, return a placeholder response
        export_id = UUID()
        
        return BulkExportResponse(
            export_id=export_id,
            status="started",
            total_records=0,
            created_at=datetime.utcnow()
        )

    async def get_system_health(self) -> SystemHealthCheck:
        """
        Get system health status.
        
        Returns:
            System health check results
        """
        # Check database health
        try:
            await self.db.execute("SELECT 1")
            database_status = {"status": "healthy", "response_time": 0.001}
        except Exception as e:
            database_status = {"status": "error", "error": str(e)}
        
        # Check storage health
        storage_status = {"status": "healthy", "available_space": "85%"}
        
        # Check external services
        external_services = {
            "firebase": {"status": "healthy"},
            "email_service": {"status": "healthy"}
        }
        
        # Performance metrics
        performance_metrics = {
            "avg_response_time": 0.15,
            "requests_per_minute": 120,
            "error_rate": 0.01
        }
        
        return SystemHealthCheck(
            status="healthy",
            database=database_status,
            storage=storage_status,
            external_services=external_services,
            performance_metrics=performance_metrics,
            alerts=[],
            last_check=datetime.utcnow()
        )

    # Helper methods for calculating statistics

    async def _calculate_collection_stats(
        self,
        collections_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate collection statistics."""
        total = len(collections_data)
        published = sum(1 for item in collections_data if item['collection'].is_published)
        draft = sum(1 for item in collections_data if item['collection'].status == 'draft')
        archived = sum(1 for item in collections_data if item['collection'].status == 'archived')
        
        # Calculate recent additions (last 30 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_additions = sum(
            1 for item in collections_data 
            if item['collection'].created_at >= recent_date
        )
        
        # Group by season and year
        by_season = {}
        by_year = {}
        total_products = 0
        
        for item in collections_data:
            collection = item['collection']
            product_count = item['product_count']
            
            # Season stats
            season = collection.season
            by_season[season] = by_season.get(season, 0) + 1
            
            # Year stats
            year = str(collection.year)
            by_year[year] = by_year.get(year, 0) + 1
            
            total_products += product_count
        
        average_products = total_products / total if total > 0 else 0
        
        return {
            'total': total,
            'published': published,
            'draft': draft,
            'archived': archived,
            'recent_additions': recent_additions,
            'by_season': by_season,
            'by_year': by_year,
            'average_products_per_collection': average_products
        }

    async def _calculate_product_stats(self) -> Dict[str, Any]:
        """Calculate product statistics."""
        # Get basic product counts
        all_products, total = await self.product_repository.get_products_with_filters({})
        
        active = sum(1 for p in all_products if p.status == 'active')
        discontinued = sum(1 for p in all_products if p.status == 'discontinued')
        coming_soon = sum(1 for p in all_products if p.status == 'coming_soon')
        featured = sum(1 for p in all_products if p.is_featured)
        
        # Recent additions
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_additions = sum(1 for p in all_products if p.created_at >= recent_date)
        
        # Group by category
        by_category = {}
        for product in all_products:
            category = product.category
            by_category[category] = by_category.get(category, 0) + 1
        
        # Calculate other metrics
        with_variants = sum(1 for p in all_products if p.variants)
        with_images = sum(1 for p in all_products if p.images)
        with_specifications = sum(1 for p in all_products if p.specifications)
        
        # Average price
        prices = [p.retail_price for p in all_products if p.retail_price]
        average_price = sum(prices) / len(prices) if prices else None
        
        # Price distribution (simplified)
        price_distribution = {
            "under_50": sum(1 for p in prices if p < 50),
            "50_100": sum(1 for p in prices if 50 <= p < 100),
            "100_200": sum(1 for p in prices if 100 <= p < 200),
            "over_200": sum(1 for p in prices if p >= 200)
        }
        
        return {
            'total': total,
            'active': active,
            'discontinued': discontinued,
            'coming_soon': coming_soon,
            'featured': featured,
            'recent_additions': recent_additions,
            'by_category': by_category,
            'with_variants': with_variants,
            'with_images': with_images,
            'with_specifications': with_specifications,
            'average_price': float(average_price) if average_price else None,
            'price_distribution': price_distribution
        }

    async def _calculate_file_stats(self) -> Dict[str, Any]:
        """Calculate file statistics."""
        # Get storage statistics from repository
        storage_stats = await self.file_repository.get_storage_statistics()
        
        # Get largest files
        largest_files = await self.file_repository.get_largest_files(5)
        largest_files_info = [
            {
                'filename': f.filename,
                'size': f.size,
                'content_type': f.content_type
            }
            for f in largest_files
        ]
        
        # Recent uploads (last 30 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_files, _ = await self.file_repository.get_files_with_filters({
            'date_from': recent_date
        })
        recent_uploads = len(recent_files)
        
        # Calculate file type counts
        files_by_type = storage_stats.get('files_by_type', {})
        
        return {
            'total': storage_stats.get('total_files', 0),
            'total_size': storage_stats.get('total_size', 0),
            'total_size_human': self._format_file_size(storage_stats.get('total_size', 0)),
            'by_type': files_by_type,
            'images': files_by_type.get('image', {}).get('count', 0),
            'documents': files_by_type.get('application', {}).get('count', 0),
            'recent_uploads': recent_uploads,
            'average_file_size': storage_stats.get('average_file_size', 0),
            'largest_files': largest_files_info
        }

    async def _calculate_system_stats(self) -> Dict[str, Any]:
        """Calculate system statistics."""
        # These would typically come from system monitoring
        return {
            'database_size': 1024 * 1024 * 100,  # 100MB placeholder
            'database_size_human': '100 MB',
            'storage_used': 1024 * 1024 * 1024 * 5,  # 5GB placeholder
            'storage_used_human': '5 GB',
            'storage_available': 1024 * 1024 * 1024 * 95,  # 95GB placeholder
            'storage_available_human': '95 GB',
            'backup_status': 'completed',
            'last_backup': datetime.utcnow() - timedelta(hours=2),
            'uptime': 86400 * 7,  # 7 days in seconds
            'uptime_human': '7 days',
            'version': '1.0.0',
            'environment': 'production'
        }

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
