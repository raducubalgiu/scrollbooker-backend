from fastapi import HTTPException
from sqlalchemy import select, and_
from starlette import status
from starlette.requests import Request
from core.dependencies import DBSession
from models import Post, Like
from core.logger import logger

async def like_post_by_id(db: DBSession, post_id: int, request: Request):
    auth_user_id = request.state.user.get("id")

    try:
        stmt = select(Like).where(
            and_(
                Like.user_id == auth_user_id,
                Like.post_id == post_id
            )
        )

        existing = await db.execute(stmt)

        if existing.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post already liked"
            )

        bookmark = Like(user_id=auth_user_id, post_id=post_id)
        db.add(bookmark)

        post = await db.get(Post, post_id)

        post.like_count = post.like_count + 1

        db.add(post)

        await db.commit()

        return {"detail": "Post was liked successfully"}
    except Exception as e:
        await db.rollback()
        logger.error(f"Post could not be liked: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )

async def unlike_post_by_id(db: DBSession, post_id: int, request: Request):
    auth_user_id = request.state.user.get("id")

    try:
        stmt = select(Like).where(
            and_(
                Like.user_id == auth_user_id,
                Like.post_id == post_id
            )
        )

        result = await db.execute(stmt)
        like = result.scalar_one_or_none()

        if not like:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Like not found"
            )

        post = await db.get(Post, post_id)

        if post.like_count > 0:
            post.like_count = post.like_count - 1

        db.add(post)

        await db.delete(like)
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Post could not be liked: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )

    return { "detail": "Like removed" }