from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
    poolclass=NullPool if settings.ENV == "test" else None,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    pool_recycle=300,
)

# Create sync engine for Alembic migrations
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+asyncpg", ""),  # Remove asyncpg driver for sync engine
    echo=settings.DB_ECHO,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    pool_recycle=300,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=settings.DB_EXPIRE_ON_COMMIT,
    autocommit=False,
    autoflush=False,
)

# Create declarative base
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    Used for testing and development.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """
    Drop all database tables.
    Used for testing cleanup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)