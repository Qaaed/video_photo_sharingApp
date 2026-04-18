from pydantic import BaseModel
from fastapi_users import schemas
import uuid

# Schema for creating a post (not currently used in endpoints)
class PostCreate(BaseModel):
    title: str
    content: str

# Schema for post responses (not currently used in endpoints)
class PostResponse(BaseModel):
    title: str
    content: str

# User read schema - used in API responses
class UserRead(schemas.BaseUser[uuid.UUID]):
    """Schema for user data returned in API responses."""
    pass

# User creation schema - used in registration
class UserCreate(schemas.BaseUserCreate):
    """Schema for user registration with email and password."""
    pass

# User update schema - used for updating user profile
class UserUpdate(schemas.BaseUserUpdate):
    """Schema for user profile updates."""
    pass