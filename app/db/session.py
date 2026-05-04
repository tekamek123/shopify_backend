from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Create async engine
# Note: DATABASE_URL should use postgresql+asyncpg://
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True, # Recommended for handling stale connections
)

# Create sessionmaker
# Using async_sessionmaker (SQLAlchemy 2.0 style)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy models.
    """
    pass
