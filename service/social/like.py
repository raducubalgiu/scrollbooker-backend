from enum import Enum

from fastapi import HTTPException, Request, Response, status
from sqlalchemy import select, and_, insert, update, func, delete

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from models import Post, Like
from core.logger import logger
from schema.social.post import UserPostResponse
from service.social.util.fetch_paginated_posts import fetch_paginated_posts
from service.social.util.is_post_actioned import is_post_actioned

class LikeTypeEnum(str, Enum):
    LIKE = "LIKE"
    UNLIKE = "UNLIKE"

async def _update_post_like_counter(db: DBSession, post_id: int, action_type: LikeTypeEnum,) -> None:
    delta = 1 if action_type == LikeTypeEnum.LIKE else -1

    await db.execute(
        update(Post)
        .where(Post.id == post_id)
        .values(like_count=func.greatest(Post.like_count + delta, 0))
    )

async def get_posts_liked_by_user_id(
        db: DBSession,
        user_id: int,
        pagination: Pagination,
        request: Request
) -> PaginatedResponse[UserPostResponse]:
    auth_user_id = request.state.user.get("id")

    base_ids = (
        select(Post.id)
        .join(Like, Post.id == Like.post_id)
        .where(Like.user_id == user_id)
    )

    return await fetch_paginated_posts(
        db=db,
        auth_user_id=auth_user_id,
        pagination=pagination,
        base_post_ids_query=base_ids
    )

async def like_post_by_id(db: DBSession, post_id: int, request: Request) -> Response:
    auth_user_id = request.state.user.get("id")

    try:
        async with db.begin():
            is_post_liked = await is_post_actioned(db, Like, post_id, auth_user_id)

            if is_post_liked:
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
            is_post_liked = await is_post_actioned(db, Like, post_id, auth_user_id)

            if not is_post_liked:
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