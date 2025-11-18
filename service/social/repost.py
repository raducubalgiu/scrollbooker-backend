from fastapi import HTTPException, Request, status, Response
from sqlalchemy import select, and_, insert, delete

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination, AuthenticatedUser
from models import Repost
from models.social.post import Post
from schema.social.post import UserPostResponse
from schema.social.repost import RepostCreate
from service.social.util.fetch_paginated_posts import fetch_paginated_posts
from service.social.util.is_post_actioned import is_post_actioned
from service.social.util.update_post_counter import update_post_counter, PostActionEnum

async def get_reposts_by_user(
        db: DBSession,
        user_id: int,
        pagination: Pagination,
        auth_user: AuthenticatedUser
) -> PaginatedResponse[UserPostResponse]:
    auth_user_id = auth_user.id

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
        auth_user: AuthenticatedUser
) -> Response:
    async with db.begin():
        auth_user_id = auth_user.id

        post = await db.get(Post, post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        is_post_reposted = await is_post_actioned(db, Repost, post_id, auth_user_id)

        if is_post_reposted:
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

        await update_post_counter(db, Repost, post_id, PostActionEnum.ADD)

        return Response(status_code=status.HTTP_201_CREATED)

async def un_repost_post_by_id(
        db: DBSession,
        post_id: int,
        auth_user: AuthenticatedUser
) -> Response:
    async with db.begin():
        auth_user_id = auth_user.id

        is_post_reposted = await is_post_actioned(db, Repost, post_id, auth_user_id)

        if not is_post_reposted:
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

        await update_post_counter(db, Repost, post_id, PostActionEnum.REMOVE)

        return Response(status_code=status.HTTP_204_NO_CONTENT)