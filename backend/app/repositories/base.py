"""
Base Repository Pattern

Provides common database operations with proper separation of concerns.
All business logic should be in services, not repositories or models.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import Select

from app.models.base import BaseModel
from app.core.exceptions import NotFoundError, ValidationError

# Generic type for model classes
ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType], ABC):
    """
    Abstract base repository with common CRUD operations.
    
    This repository provides standard database operations while maintaining
    clean separation between data access and business logic.
    """

    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        """
        Initialize repository with database session and model class.
        
        Args:
            db: Async SQLAlchemy session
            model: SQLAlchemy model class
        """
        self.db = db
        self.model = model

    async def get_by_id(
        self, 
        id: UUID, 
        include_deleted: bool = False,
        load_relations: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            id: Record UUID
            include_deleted: Whether to include soft-deleted records
            load_relations: List of relationships to eager load
            
        Returns:
            Model instance or None if not found
        """
        query = select(self.model).where(self.model.id == id)
        
        # Apply soft deletion filter
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.where(self.model.is_deleted == False)
        
        # Apply eager loading
        if load_relations:
            query = self._apply_eager_loading(query, load_relations)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_field(
        self,
        field_name: str,
        field_value: Any,
        include_deleted: bool = False,
        load_relations: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """
        Get a single record by any field.
        
        Args:
            field_name: Name of the field to filter by
            field_value: Value to match
            include_deleted: Whether to include soft-deleted records
            load_relations: List of relationships to eager load
            
        Returns:
            Model instance or None if not found
        """
        field = getattr(self.model, field_name)
        query = select(self.model).where(field == field_value)
        
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.where(self.model.is_deleted == False)
            
        if load_relations:
            query = self._apply_eager_loading(query, load_relations)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        load_relations: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted records
            load_relations: List of relationships to eager load
            order_by: Field name to order by (prefix with '-' for desc)
            filters: Dictionary of field filters
            
        Returns:
            List of model instances
        """
        query = select(self.model)
        
        # Apply soft deletion filter
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.where(self.model.is_deleted == False)
        
        # Apply custom filters
        if filters:
            query = self._apply_filters(query, filters)
        
        # Apply ordering
        if order_by:
            query = self._apply_ordering(query, order_by)
        else:
            # Default ordering by created_at desc
            if hasattr(self.model, 'created_at'):
                query = query.order_by(self.model.created_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Apply eager loading
        if load_relations:
            query = self._apply_eager_loading(query, load_relations)
        
        result = await self.db.execute(query)
        # Use unique() when eager loading to handle JOINs properly
        if load_relations:
            return result.scalars().unique().all()
        else:
            return result.scalars().all()

    async def count(
        self,
        include_deleted: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count records with optional filters.
        
        Args:
            include_deleted: Whether to include soft-deleted records
            filters: Dictionary of field filters
            
        Returns:
            Number of matching records
        """
        query = select(func.count(self.model.id))
        
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.where(self.model.is_deleted == False)
        
        if filters:
            query = self._apply_filters(query, filters)
        
        result = await self.db.execute(query)
        return result.scalar()

    async def create(self, data: Dict[str, Any], user_id: Optional[str] = None) -> ModelType:  # Firebase UID
        """
        Create a new record.
        
        Args:
            data: Dictionary of field values
            user_id: ID of user creating the record
            
        Returns:
            Created model instance
        """
        # Add audit fields if they exist
        if hasattr(self.model, 'created_by') and user_id:
            data['created_by'] = user_id
        
        instance = self.model(**data)
        self.db.add(instance)
        await self.db.flush()  # Get the ID without committing
        await self.db.refresh(instance)  # Refresh to get all computed fields
        
        return instance

    async def update(
        self, 
        id: UUID, 
        data: Dict[str, Any], 
        user_id: Optional[UUID] = None
    ) -> Optional[ModelType]:
        """
        Update an existing record.
        
        Args:
            id: Record UUID
            data: Dictionary of updated field values
            user_id: ID of user updating the record
            
        Returns:
            Updated model instance or None if not found
        """
        # Add audit fields if they exist
        if hasattr(self.model, 'updated_by') and user_id:
            data['updated_by'] = user_id
        
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**data)
            .returning(self.model.id)
        )
        
        # Apply soft deletion filter
        if hasattr(self.model, 'is_deleted'):
            query = query.where(self.model.is_deleted == False)
        
        result = await self.db.execute(query)
        updated_id = result.scalar_one_or_none()
        
        if updated_id:
            return await self.get_by_id(updated_id)
        return None

    async def delete(self, id: UUID, user_id: Optional[UUID] = None, soft: bool = True) -> bool:
        """
        Delete a record (soft delete by default).
        
        Args:
            id: Record UUID
            user_id: ID of user deleting the record
            soft: Whether to perform soft delete (if supported by model)
            
        Returns:
            True if record was deleted, False if not found
        """
        if soft and hasattr(self.model, 'is_deleted'):
            # Soft delete
            from datetime import datetime
            update_data = {
                'is_deleted': True,
                'deleted_at': datetime.utcnow()
            }
            if hasattr(self.model, 'updated_by') and user_id:
                update_data['updated_by'] = user_id
            
            result = await self.update(id, update_data, user_id)
            return result is not None
        else:
            # Hard delete
            query = delete(self.model).where(self.model.id == id)
            result = await self.db.execute(query)
            return result.rowcount > 0

    async def restore(self, id: UUID, user_id: Optional[UUID] = None) -> Optional[ModelType]:
        """
        Restore a soft-deleted record.
        
        Args:
            id: Record UUID
            user_id: ID of user restoring the record
            
        Returns:
            Restored model instance or None if not found
        """
        if not hasattr(self.model, 'is_deleted'):
            raise ValidationError("Model does not support soft deletion")
        
        update_data = {
            'is_deleted': False,
            'deleted_at': None
        }
        if hasattr(self.model, 'updated_by') and user_id:
            update_data['updated_by'] = user_id
        
        query = (
            update(self.model)
            .where(and_(self.model.id == id, self.model.is_deleted == True))
            .values(**update_data)
            .returning(self.model.id)
        )
        
        result = await self.db.execute(query)
        restored_id = result.scalar_one_or_none()
        
        if restored_id:
            return await self.get_by_id(restored_id)
        return None

    async def exists(
        self, 
        id: UUID, 
        include_deleted: bool = False
    ) -> bool:
        """
        Check if a record exists.
        
        Args:
            id: Record UUID
            include_deleted: Whether to include soft-deleted records
            
        Returns:
            True if record exists, False otherwise
        """
        query = select(func.count(self.model.id)).where(self.model.id == id)
        
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.where(self.model.is_deleted == False)
        
        result = await self.db.execute(query)
        count = result.scalar()
        return count > 0

    async def bulk_create(
        self, 
        data_list: List[Dict[str, Any]], 
        user_id: Optional[UUID] = None
    ) -> List[ModelType]:
        """
        Create multiple records in bulk.
        
        Args:
            data_list: List of dictionaries with field values
            user_id: ID of user creating the records
            
        Returns:
            List of created model instances
        """
        instances = []
        
        for data in data_list:
            if hasattr(self.model, 'created_by') and user_id:
                data['created_by'] = user_id
            
            instance = self.model(**data)
            instances.append(instance)
        
        self.db.add_all(instances)
        await self.db.flush()
        
        for instance in instances:
            await self.db.refresh(instance)
        
        return instances

    def _apply_filters(self, query: Select, filters: Dict[str, Any]) -> Select:
        """
        Apply filters to query.
        
        Args:
            query: SQLAlchemy select query
            filters: Dictionary of field filters
            
        Returns:
            Updated query with filters applied
        """
        for field_name, field_value in filters.items():
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                
                # Handle different filter types
                if isinstance(field_value, dict):
                    # Advanced filters like {"gte": 100}, {"in": [1,2,3]}
                    for op, value in field_value.items():
                        if op == 'gte':
                            query = query.where(field >= value)
                        elif op == 'lte':
                            query = query.where(field <= value)
                        elif op == 'gt':
                            query = query.where(field > value)
                        elif op == 'lt':
                            query = query.where(field < value)
                        elif op == 'in':
                            query = query.where(field.in_(value))
                        elif op == 'like':
                            query = query.where(field.like(f"%{value}%"))
                        elif op == 'ilike':
                            query = query.where(field.ilike(f"%{value}%"))
                elif isinstance(field_value, list):
                    # List means "in" filter
                    query = query.where(field.in_(field_value))
                else:
                    # Simple equality
                    query = query.where(field == field_value)
        
        return query

    def _apply_ordering(self, query: Select, order_by: str) -> Select:
        """
        Apply ordering to query.
        
        Args:
            query: SQLAlchemy select query
            order_by: Field name (prefix with '-' for descending)
            
        Returns:
            Updated query with ordering applied
        """
        if order_by.startswith('-'):
            # Descending order
            field_name = order_by[1:]
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                query = query.order_by(field.desc())
        else:
            # Ascending order
            if hasattr(self.model, order_by):
                field = getattr(self.model, order_by)
                query = query.order_by(field.asc())
        
        return query

    def _apply_eager_loading(
        self, 
        query: Select, 
        load_relations: List[str]
    ) -> Select:
        """
        Apply eager loading to query.
        
        Args:
            query: SQLAlchemy select query
            load_relations: List of relationships to eager load
            
        Returns:
            Updated query with eager loading applied
        """
        for relation in load_relations:
            if hasattr(self.model, relation):
                relationship_attr = getattr(self.model, relation)
                
                # Use selectinload for collections, joinedload for single relations
                if hasattr(relationship_attr.property, 'collection') and relationship_attr.property.collection:
                    query = query.options(selectinload(relationship_attr))
                else:
                    query = query.options(joinedload(relationship_attr))
        
        return query