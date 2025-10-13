from enum import Enum

from fastapi import HTTPException, Request, status, Response
from sqlalchemy import select, func, and_, insert, update, delete

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from models import BookmarkPost, Post
from schema.social.post import UserPostResponse
from service.social.util.fetch_paginated_posts import fetch_paginated_posts
from core.logger import logger
from service.social.util.is_post_actioned import is_post_actioned


class BookmarkTypeEnum(str, Enum):
    BOOKMARK = "BOOKMARK"
    UNBOOKMARK = "UNBOOKMARK"

async def _update_post_bookmark_counter(
        db: DBSession,
        post_id: int,
        action_type: BookmarkTypeEnum
) -> None:
    delta = 1 if action_type == BookmarkTypeEnum.BOOKMARK else -1

    await db.execute(
        update(Post)
        .where(Post.id == post_id)
        .values(bookmark_count=func.greatest(Post.bookmark_count + delta, 0))
    )

async def get_bookmarked_posts_by_user(
        db: DBSession,
        user_id: int,
        pagination: Pagination,
        request: Request
) -> PaginatedResponse[UserPostResponse]:
    auth_user_id = request.state.user.get("id")

    base_ids = (
        select(Post.id)
        .join(BookmarkPost, BookmarkPost.post_id == Post.id)
        .where(BookmarkPost.user_id == user_id)
    )

    return await fetch_paginated_posts(
        db=db,
        auth_user_id=auth_user_id,
        pagination=pagination,
        base_post_ids_query=base_ids
    )

async def bookmark_post_by_id(
        db: DBSession,
        post_id: int,
        request: Request
) -> Response:
    auth_user_id = request.state.user.get("id")

    try:
        async with db.begin():
            is_post_bookmarked = await is_post_actioned(db, BookmarkPost, post_id, auth_user_id)

            if is_post_bookmarked:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Post already bookmarked"
                )

            await db.execute(
                insert(BookmarkPost)
                .values(user_id=auth_user_id, post_id=post_id))

            await _update_post_bookmark_counter(
                db=db,
                post_id=post_id,
                action_type=BookmarkTypeEnum.BOOKMARK
            )
        return Response(status_code=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Post could not be bookmarked: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )

async def unbookmark_post_by_id(db: DBSession, post_id: int, request: Request) -> Response:
    auth_user_id = request.state.user.get("id")

    try:
        async with db.begin():
            is_post_bookmarked = await is_post_actioned(db, BookmarkPost, post_id, auth_user_id)

            if not is_post_bookmarked:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bookmark not found"
                )

            await db.execute(
                delete(BookmarkPost)
                .where(and_(
                    BookmarkPost.user_id == auth_user_id,
                    BookmarkPost.post_id == post_id
                ))
            )

            await _update_post_bookmark_counter(
                db=db,
                post_id=post_id,
                action_type=BookmarkTypeEnum.UNBOOKMARK
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Post could not be unbookmarked: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )