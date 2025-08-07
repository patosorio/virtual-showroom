"""
Base Service Pattern

Contains business logic and orchestrates between repositories.
Services are the only place where business rules should live.
"""

from abc import ABC
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel
from app.repositories.base import BaseRepository
from app.core.exceptions import (
    NotFoundError, ValidationError, ConflictError, 
    BadRequestError, ForbiddenError
)

# Generic types
ModelType = TypeVar("ModelType", bound=BaseModel)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[ModelType, RepositoryType], ABC):
    """
    Abstract base service with common business logic patterns.
    
    Services contain all business logic and coordinate between repositories.
    They validate business rules, handle complex operations, and ensure data integrity.
    """

    def __init__(self, db: AsyncSession, repository: Type[RepositoryType], model: Type[ModelType]):
        """
        Initialize service with database session and repository.
        
        Args:
            db: Async SQLAlchemy session
            repository: Repository class for data access
            model: Model class for type hints
        """
        self.db = db
        self.repository = repository(db, model)
        self.model = model

    async def get_by_id(
        self, 
        id: UUID, 
        user_id: Optional[UUID] = None,
        load_relations: Optional[List[str]] = None
    ) -> ModelType:
        """
        Get entity by ID with business logic validation.
        
        Args:
            id: Entity UUID
            user_id: ID of requesting user (for permission checks)
            load_relations: List of relationships to eager load
            
        Returns:
            Model instance
            
        Raises:
            NotFoundError: If entity doesn't exist
            ForbiddenError: If user doesn't have permission
        """
        entity = await self.repository.get_by_id(id, load_relations=load_relations)
        
        if not entity:
            raise NotFoundError(
                detail=f"{self.model.__name__} with ID {id} not found",
                error_code=f"{self.model.__name__.upper()}_NOT_FOUND",
                context={"id": str(id)}
            )
        
        # Apply business logic permission checks
        await self._check_read_permission(entity, user_id)
        
        return entity

    async def get_by_field(
        self,
        field_name: str,
        field_value: Any,
        user_id: Optional[UUID] = None,
        load_relations: Optional[List[str]] = None
    ) -> ModelType:
        """
        Get entity by any field with business validation.
        
        Args:
            field_name: Name of the field to search by
            field_value: Value to match
            user_id: ID of requesting user
            load_relations: List of relationships to eager load
            
        Returns:
            Model instance
            
        Raises:
            NotFoundError: If entity doesn't exist
            ForbiddenError: If user doesn't have permission
        """
        entity = await self.repository.get_by_field(
            field_name, field_value, load_relations=load_relations
        )
        
        if not entity:
            raise NotFoundError(
                detail=f"{self.model.__name__} with {field_name}='{field_value}' not found",
                error_code=f"{self.model.__name__.upper()}_NOT_FOUND",
                context={field_name: field_value}
            )
        
        await self._check_read_permission(entity, user_id)
        
        return entity

    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        user_id: Optional[UUID] = None,
        load_relations: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[ModelType], int]:
        """
        List entities with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            user_id: ID of requesting user
            load_relations: List of relationships to eager load
            order_by: Field name to order by
            filters: Dictionary of field filters
            
        Returns:
            Tuple of (entities list, total count)
        """
        # Apply business logic filters
        business_filters = await self._apply_business_filters(filters, user_id)
        
        # Validate pagination parameters
        await self._validate_pagination(skip, limit)
        
        # Get entities and count
        entities = await self.repository.get_all(
            skip=skip,
            limit=limit,
            load_relations=load_relations,
            order_by=order_by,
            filters=business_filters
        )
        
        total = await self.repository.count(filters=business_filters)
        
        return entities, total

    async def create(
        self, 
        data: Dict[str, Any], 
        user_id: Optional[UUID] = None
    ) -> ModelType:
        """
        Create new entity with business validation.
        
        Args:
            data: Entity data
            user_id: ID of creating user
            
        Returns:
            Created model instance
            
        Raises:
            ValidationError: If data is invalid
            ConflictError: If entity already exists
            ForbiddenError: If user doesn't have permission
        """
        # Check creation permission
        await self._check_create_permission(data, user_id)
        
        # Validate business rules
        await self._validate_create_data(data, user_id)
        
        # Check for conflicts (e.g., unique constraints)
        await self._check_create_conflicts(data)
        
        # Process data (e.g., generate slugs, set defaults)
        processed_data = await self._process_create_data(data, user_id)
        
        # Create entity
        entity = await self.repository.create(processed_data, user_id)
        
        # Post-creation business logic
        await self._post_create_actions(entity, user_id)
        
        return entity

    async def update(
        self, 
        id: UUID, 
        data: Dict[str, Any], 
        user_id: Optional[UUID] = None
    ) -> ModelType:
        """
        Update existing entity with business validation.
        
        Args:
            id: Entity UUID
            data: Updated entity data
            user_id: ID of updating user
            
        Returns:
            Updated model instance
            
        Raises:
            NotFoundError: If entity doesn't exist
            ValidationError: If data is invalid
            ConflictError: If update creates conflicts
            ForbiddenError: If user doesn't have permission
        """
        # Get existing entity
        existing = await self.repository.get_by_id(id)
        if not existing:
            raise NotFoundError(
                detail=f"{self.model.__name__} with ID {id} not found",
                error_code=f"{self.model.__name__.upper()}_NOT_FOUND",
                context={"id": str(id)}
            )
        
        # Check update permission
        await self._check_update_permission(existing, data, user_id)
        
        # Validate business rules
        await self._validate_update_data(existing, data, user_id)
        
        # Check for conflicts
        await self._check_update_conflicts(existing, data)
        
        # Process data
        processed_data = await self._process_update_data(existing, data, user_id)
        
        # Update entity
        entity = await self.repository.update(id, processed_data, user_id)
        
        # Post-update business logic
        await self._post_update_actions(existing, entity, user_id)
        
        return entity

    async def delete(
        self, 
        id: UUID, 
        user_id: Optional[UUID] = None,
        soft: bool = True
    ) -> bool:
        """
        Delete entity with business validation.
        
        Args:
            id: Entity UUID
            user_id: ID of deleting user
            soft: Whether to perform soft delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundError: If entity doesn't exist
            ForbiddenError: If user doesn't have permission
            ConflictError: If entity cannot be deleted
        """
        # Get existing entity
        existing = await self.repository.get_by_id(id)
        if not existing:
            raise NotFoundError(
                detail=f"{self.model.__name__} with ID {id} not found",
                error_code=f"{self.model.__name__.upper()}_NOT_FOUND",
                context={"id": str(id)}
            )
        
        # Check delete permission
        await self._check_delete_permission(existing, user_id)
        
        # Validate deletion is allowed
        await self._validate_delete(existing, user_id)
        
        # Pre-deletion business logic
        await self._pre_delete_actions(existing, user_id)
        
        # Delete entity
        success = await self.repository.delete(id, user_id, soft)
        
        if success:
            # Post-deletion business logic
            await self._post_delete_actions(existing, user_id)
        
        return success

    async def restore(
        self, 
        id: UUID, 
        user_id: Optional[UUID] = None
    ) -> ModelType:
        """
        Restore soft-deleted entity.
        
        Args:
            id: Entity UUID
            user_id: ID of restoring user
            
        Returns:
            Restored model instance
            
        Raises:
            NotFoundError: If entity doesn't exist
            ForbiddenError: If user doesn't have permission
            ValidationError: If entity cannot be restored
        """
        # Check restore permission
        await self._check_restore_permission(id, user_id)
        
        # Restore entity
        entity = await self.repository.restore(id, user_id)
        
        if not entity:
            raise NotFoundError(
                detail=f"{self.model.__name__} with ID {id} not found or not deleted",
                error_code=f"{self.model.__name__.upper()}_NOT_FOUND",
                context={"id": str(id)}
            )
        
        # Post-restoration business logic
        await self._post_restore_actions(entity, user_id)
        
        return entity

    async def bulk_create(
        self,
        data_list: List[Dict[str, Any]],
        user_id: Optional[UUID] = None
    ) -> List[ModelType]:
        """
        Create multiple entities with business validation.
        
        Args:
            data_list: List of entity data dictionaries
            user_id: ID of creating user
            
        Returns:
            List of created model instances
        """
        # Check bulk create permission
        await self._check_bulk_create_permission(data_list, user_id)
        
        # Validate all data
        for i, data in enumerate(data_list):
            try:
                await self._validate_create_data(data, user_id)
                await self._check_create_conflicts(data)
            except Exception as e:
                raise ValidationError(
                    detail=f"Validation failed for item {i}: {str(e)}",
                    context={"item_index": i, "data": data}
                )
        
        # Process all data
        processed_data_list = []
        for data in data_list:
            processed_data = await self._process_create_data(data, user_id)
            processed_data_list.append(processed_data)
        
        # Create entities
        entities = await self.repository.bulk_create(processed_data_list, user_id)
        
        # Post-creation business logic for each entity
        for entity in entities:
            await self._post_create_actions(entity, user_id)
        
        return entities

    # Business Logic Hooks (Override in subclasses)
    
    async def _check_read_permission(
        self, 
        entity: ModelType, 
        user_id: Optional[UUID]
    ) -> None:
        """Override to implement read permission checks."""
        pass

    async def _check_create_permission(
        self, 
        data: Dict[str, Any], 
        user_id: Optional[UUID]
    ) -> None:
        """Override to implement create permission checks."""
        pass

    async def _check_update_permission(
        self, 
        entity: ModelType, 
        data: Dict[str, Any], 
        user_id: Optional[UUID]
    ) -> None:
        """Override to implement update permission checks."""
        pass

    async def _check_delete_permission(
        self, 
        entity: ModelType, 
        user_id: Optional[UUID]
    ) -> None:
        """Override to implement delete permission checks."""
        pass

    async def _check_restore_permission(
        self, 
        id: UUID, 
        user_id: Optional[UUID]
    ) -> None:
        """Override to implement restore permission checks."""
        pass

    async def _check_bulk_create_permission(
        self,
        data_list: List[Dict[str, Any]],
        user_id: Optional[UUID]
    ) -> None:
        """Override to implement bulk create permission checks."""
        for data in data_list:
            await self._check_create_permission(data, user_id)

    async def _validate_create_data(
        self, 
        data: Dict[str, Any], 
        user_id: Optional[UUID]
    ) -> None:
        """Override to implement create data validation."""
        pass

    async def _validate_update_data(
        self, 
        entity: ModelType, 
        data: Dict[str, Any], 
        user_id: Optional[UUID]
    ) -> None:
        """Override to implement update data validation."""
        pass

    async def _validate_delete(
        self, 
        entity: ModelType, 
        user_id: Optional[UUID]
    ) -> None:
        """Override to implement delete validation."""
        pass

    async def _check_create_conflicts(self, data: Dict[str, Any]) -> None:
        """Override to check for creation conflicts (e.g., unique constraints)."""
        pass

    async def _check_update_conflicts(
        self, 
        entity: ModelType, 
        data: Dict[str, Any]
    ) -> None:
        """Override to check for update conflicts."""
        pass

    async def _process_create_data(
        self, 
        data: Dict[str, Any], 
        user_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Override to process data before creation (e.g., generate slugs)."""
        return data

    async def _process_update_data(
        self, 
        entity: ModelType, 
        data: Dict[str, Any], 
        user_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Override to process data before update."""
        return data

    async def _apply_business_filters(
        self, 
        filters: Optional[Dict[str, Any]], 
        user_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Override to apply business logic filters (e.g., user-specific data)."""
        return filters or {}

    async def _post_create_actions(
        self, 
        entity: ModelType, 
        user_id: Optional[UUID]
    ) -> None:
        """Override to implement post-creation business logic."""
        pass

    async def _post_update_actions(
        self, 
        old_entity: ModelType, 
        new_entity: ModelType, 
        user_id: Optional[UUID]
    ) -> None:
        """Override to implement post-update business logic."""
        pass

    async def _pre_delete_actions(
        self, 
        entity: ModelType, 
        user_id: Optional[UUID]
    ) -> None:
        """Override to implement pre-deletion business logic."""
        pass

    async def _post_delete_actions(
        self,
        entity: ModelType,
        user_id: Optional[UUID]
    ) -> None:
        """Override to implement post-deletion business logic."""
        pass