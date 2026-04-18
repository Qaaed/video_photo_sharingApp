from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
from app.db import Post, create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
import shutil
import os
import uuid
import tempfile
from app.users import auth_backend, current_active_user, fastapi_users


# Lifespan context manager - runs on app startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database and create tables on startup
    await create_db_and_tables()
    yield
    # Cleanup happens after yield (when app shuts down)

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt', tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

@app.post("/upload")
async def upload_file(
        file: UploadFile = File(...),
        caption: str = Form(""),
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)
):
    """Upload a media file (image or video) and create a post."""
    temp_file_path = None

    try:
        # Create a temporary file to store the uploaded content
        # This is needed because ImageKit requires a file object to read from
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            # Copy the uploaded file content to the temporary file
            shutil.copyfileobj(file.file, temp_file)

        # Upload the file to ImageKit cloud storage
        upload_result = imagekit.files.upload(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            use_unique_file_name=True,
            tags=["backend-upload"]
        )

        # If upload was successful, create a database record for the post
        if upload_result:
            # Create a post record with the uploaded file's URL and metadata
            post = Post(
                user_id=user.id,
                caption=caption,
                url=upload_result.url,
                file_type="video" if file.content_type.startswith("video/") else "image",
                file_name=upload_result.name
            )
            # Save the post to the database
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post

    except Exception as e:
        # Return error if upload fails
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up: delete temporary file and close file handle
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()

@app.get("/feed")
async def get_feed(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    """Get the feed with all posts sorted by most recent first."""
    # Fetch all posts ordered by creation date (newest first)
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    # Fetch all users and create a lookup dictionary for email by user ID
    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {u.id: u.email for u in users}

    # Format posts for response, including owner information and email
    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,  # Check if current user owns this post
                "email": user_dict.get(post.user_id, "Unknown")
            }
        )

    return {"posts": posts_data}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user),):
    """Delete a post if the current user is the owner."""
    try:
        # Convert string ID to UUID
        post_uuid = uuid.UUID(post_id)

        # Fetch the post from database
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        # Check if post exists
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Verify the current user owns this post before deletion
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You don't have permission to delete this post")

        # Delete the post from database
        await session.delete(post)
        await session.commit()

        return {"success": True, "message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
