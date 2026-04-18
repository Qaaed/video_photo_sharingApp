from collections.abc import AsyncGenerator
import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends

# SQLite database URL - uses aiosqlite for async operations
DATABASE_URL = "sqlite+aiosqlite:///./test.db"


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model - extends FastAPI Users base user with UUID ID."""
    posts = relationship("Post", back_populates="user")


class Post(Base):
    """Post model - represents a user's shared media (image or video)."""
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)  # Foreign key to user
    caption = Column(Text)  # Post description/text
    url = Column(String, nullable=False)  # ImageKit URL of the media
    file_type = Column(String, nullable=False)  # "image" or "video"
    file_name = Column(String, nullable=False)  # Original filename from upload
    created_at = Column(DateTime, default=datetime.utcnow)  # Creation timestamp

    user = relationship("User", back_populates="posts")


# Create async engine for database connections
engine = create_async_engine(DATABASE_URL)
# Create session maker for creating new sessions
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    """Create all database tables (called on app startup)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get an async database session for API endpoints."""
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)