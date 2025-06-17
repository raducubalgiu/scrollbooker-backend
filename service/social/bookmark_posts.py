from fastapi import HTTPException
from starlette.requests import Request
from starlette import status
from sqlalchemy import select
from backend.core.dependencies import DBSession
from backend.models import BookmarkPost

async def bookmark_post_by_id(db: DBSession, post_id: int, request: Request):
    auth_user_id = request.state.user.get("id")

    stmt = select(BookmarkPost).where(
        BookmarkPost.user_id == auth_user_id,
        BookmarkPost.post_id == post_id
    )

    existing = await db.execute(stmt)

    if existing.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already bookmarked"
        )

    bookmark = BookmarkPost(user_id=auth_user_id, post_id=post_id)
    db.add(bookmark)
    await db.commit()

    return { "detail": "Post was bookmarked successfully" }

async def unbookmark_post_by_id(db: DBSession, post_id: int, request: Request):
    auth_user_id = request.state.user.get("id")

    stmt = select(BookmarkPost).where(
        BookmarkPost.user_id == auth_user_id,
        BookmarkPost.post_id == post_id
    )

    result = await db.execute(stmt)
    bookmark = result.scalar_one_or_none()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bookmark not found"
        )

    await db.delete(bookmark)
    await db.commit()

    return { "detail": "Bookmark removed" }