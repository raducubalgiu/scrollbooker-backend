from fastapi import HTTPException, Request, status, Response
from sqlalchemy import select, and_, insert, delete

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from models import BookmarkPost, Post
from schema.social.post import UserPostResponse
from service.social.util.fetch_paginated_posts import fetch_paginated_posts
from service.social.util.is_post_actioned import is_post_actioned
from service.social.util.update_post_counter import update_post_counter, PostActionEnum

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

        await update_post_counter(db, BookmarkPost, post_id, PostActionEnum.ADD)

        return Response(status_code=status.HTTP_201_CREATED)

async def unbookmark_post_by_id(
        db: DBSession,
        post_id: int,
        request: Request
) -> Response:
    auth_user_id = request.state.user.get("id")

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

        await update_post_counter(db, BookmarkPost, post_id, PostActionEnum.REMOVE)

        return Response(status_code=status.HTTP_204_NO_CONTENT)