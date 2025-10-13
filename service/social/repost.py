from enum import Enum

from fastapi import HTTPException, Request, status, Response
from sqlalchemy import select, func, and_, update, insert, delete

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from models import Repost
from models.social.post import Post
from schema.social.post import UserPostResponse
from schema.social.repost import RepostCreate
from service.social.fetch_paginated_posts import fetch_paginated_posts
from core.logger import logger

class RepostTypeEnum(str, Enum):
    REPOST = "REPOST"
    UN_REPOST = "UN_REPOST"

async def _is_post_reposted(db: DBSession, post_id: int, auth_user_id: int) -> bool:
    existing = await db.execute(
        select(Repost).where(
            and_(
                Repost.user_id == auth_user_id,
                Repost.post_id == post_id
            )
        )
    )
    return True if existing.scalar() else False

async def _update_post_repost_counter(db: DBSession, post_id: int, action_type: RepostTypeEnum) -> None:
    delta = 1 if action_type == RepostTypeEnum.REPOST else -1

    await db.execute(
        update(Post)
        .where(Post.id == post_id)
        .values(repost_count=func.greatest(Post.repost_count + delta, 0))
    )

async def get_reposts_by_user(
        db: DBSession,
        user_id: int,
        pagination: Pagination,
        request: Request
) -> PaginatedResponse[UserPostResponse]:
    auth_user_id = request.state.user.get("id")

    base_ids = (
        select(Post.id)
        .join(Repost, Post.id == Repost.post_id)
        .where(Repost.user_id == user_id)
    )

    return await fetch_paginated_posts(
        db=db,
        auth_user_id=auth_user_id,
        pagination=pagination,
        base_post_ids_query=base_ids
    )

async def repost_post_by_id(
        db: DBSession,
        post_id: int,
        repost_create: RepostCreate,
        request: Request
) -> Response:
    auth_user_id = request.state.user.get("id")

    try:
        async with db.begin():
            post = await db.get(Post, post_id)

            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found"
                )

            if await _is_post_reposted(db, post_id, auth_user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Post already reposted"
                )

            await db.execute(
                insert(Repost)
                .values(
                    user_id=auth_user_id,
                    post_id=post_id,
                    original_poster_id=post.user_id,
                    comment=repost_create.comment,
                ))

            await _update_post_repost_counter(
                db=db,
                post_id=post_id,
                action_type=RepostTypeEnum.REPOST
            )
        return Response(status_code=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Post could not be reposted: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )

async def un_repost_post_by_id(db: DBSession, post_id: int, request: Request) -> Response:
    auth_user_id = request.state.user.get("id")

    try:
        async with db.begin():
            if not await _is_post_reposted(db, post_id, auth_user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Repost not found"
                )

            await db.execute(
                delete(Repost)
                .where(and_(
                    Repost.user_id == auth_user_id,
                    Repost.post_id == post_id
                ))
            )

            await _update_post_repost_counter(
                db=db,
                post_id=post_id,
                action_type=RepostTypeEnum.UN_REPOST
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.error(f"Post could not be un_reposted: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )