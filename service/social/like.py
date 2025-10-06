from enum import Enum

from fastapi import HTTPException, Request, Response, status
from sqlalchemy import select, and_, insert, update, func, delete
from core.dependencies import DBSession
from models import Post, Like
from core.logger import logger

class LikeTypeEnum(str, Enum):
    LIKE = "LIKE"
    UNLIKE = "UNLIKE"

async def _is_post_liked(db: DBSession, post_id: int, auth_user_id: int) -> bool:
    existing = await db.execute(
        select(Like).where(
            and_(
                Like.user_id == auth_user_id,
                Like.post_id == post_id
            )
        )
    )
    return True if existing.scalar() else False

async def _update_post_like_counter(db: DBSession, post_id: int, action_type: LikeTypeEnum,) -> None:
    delta = 1 if action_type == LikeTypeEnum.LIKE else -1

    await db.execute(
        update(Post)
        .where(Post.id == post_id)
        .values(like_count=func.greatest(Post.like_count + delta, 0))
    )

async def like_post_by_id(db: DBSession, post_id: int, request: Request) -> Response:
    auth_user_id = request.state.user.get("id")

    try:
        async with db.begin():
            if await _is_post_liked(db, post_id, auth_user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Post already liked"
                )

            await db.execute(
                insert(Like)
                .values(user_id=auth_user_id, post_id=post_id))

            await _update_post_like_counter(
                db=db,
                post_id=post_id,
                action_type=LikeTypeEnum.LIKE
            )
        return Response(status_code=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Post could not be liked: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )

async def unlike_post_by_id(db: DBSession, post_id: int, request: Request) -> Response:
    auth_user_id = request.state.user.get("id")

    try:
        async with db.begin():
            if not await _is_post_liked(db, post_id, auth_user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Like not found"
                )

            await db.execute(
                delete(Like)
                .where(and_(
                    Like.user_id == auth_user_id,
                    Like.post_id == post_id
                ))
            )

            await _update_post_like_counter(
                db=db,
                post_id=post_id,
                action_type=LikeTypeEnum.UNLIKE
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Post could not be liked: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )