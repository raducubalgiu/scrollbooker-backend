from operator import and_

from fastapi import HTTPException
from starlette.requests import Request
from starlette import status
from sqlalchemy import select, func, literal, desc, update

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from models import BookmarkPost, Post, Follow, User, Repost
from schema.social.post import UserPostResponse, PostProduct, PostCounters, LastMinute, PostUserActions
from schema.user.user import UserBaseMinimum
from service.social.post_media import get_post_media
from core.logger import logger

async def get_bookmarked_posts_by_user(db: DBSession, request: Request, pagination: Pagination):
    auth_user_id = request.state.user.get("id")

    count_stmt = select(func.count()).select_from(BookmarkPost).where(BookmarkPost.user_id == auth_user_id)
    count_total = await db.execute(count_stmt)
    count = count_total.scalar_one()

    is_reposted = (
        select(literal(True))
        .select_from(Repost)
        .where(and_(
            Repost.user_id == auth_user_id,
            Repost.post_id == Post.id)
        )
        .correlate(Post)
        .exists()
    )

    is_bookmarked = (
        select(literal(True))
        .select_from(BookmarkPost)
        .where(and_(
            BookmarkPost.user_id == auth_user_id,
            BookmarkPost.post_id == Post.id)
        )
        .correlate(Post)
        .exists()
    )

    is_follow = (
        select(literal(True))
        .select_from(Follow)
        .where(and_(
            Follow.follower_id == auth_user_id,
            Follow.followee_id == User.id)
        )
        .correlate(User)
        .exists()
    )

    result = await db.execute(
        select(
            Post,
            User.id,
            User.fullname,
            User.username,
            User.avatar,
            User.profession,
            is_follow,
            is_bookmarked,
            is_reposted,
        )
        .join(User, User.id == Post.user_id)
        .join(BookmarkPost, BookmarkPost.user_id == auth_user_id)
        .where(BookmarkPost.post_id == Post.id)
        .order_by(desc(Post.created_at))
        .offset((pagination.page - 1) * pagination.limit)
        .limit(pagination.limit)
    )
    posts = result.all()

    post_ids = [p.id for p, *_ in posts]
    media_map = await get_post_media(db, post_ids)

    results = []

    for post, u_id, u_fullname, u_username, u_avatar, u_profession, is_follow, is_reposted, is_bookmarked in posts:
        media_files = media_map.get(post.id, [])

        results.append(UserPostResponse(
            id=post.id,
            description=post.description,
            user=UserBaseMinimum(
                id=u_id,
                fullname=u_fullname,
                username=u_username,
                avatar=u_avatar,
                profession=u_profession,
                is_follow=is_follow
            ),
            product=PostProduct(
                id=post.product_id,
                name=post.product_name,
                description=post.product_name,
                duration=post.product_duration,
                price=post.product_price,
                price_with_discount=post.product_price_with_discount,
                discount=post.product_discount,
                currency=post.product_currency
            ),
            counters=PostCounters(
                comment_count=post.comment_count,
                like_count=post.like_count,
                bookmark_count=post.bookmark_count,
                share_count=post.share_count
            ),
            media_files=media_files,
            user_actions=PostUserActions(
                is_liked=False,
                is_bookmarked=is_bookmarked,
                is_reposted=is_reposted,
            ),
            mentions=post.mentions,
            hashtags=post.hashtags,
            bookable=post.bookable,
            instant_booking=post.instant_booking,
            last_minute=LastMinute(
                is_last_minute=post.is_last_minute,
                last_minute_end=post.last_minute_end,
                has_fixed_slots=post.has_fixed_slots,
                fixed_slots=post.fixed_slots
            ),
            created_at=post.created_at
        ))

    return PaginatedResponse(
        count=count,
        results=results
    )

async def bookmark_post_by_id(db: DBSession, post_id: int, request: Request):
    auth_user_id = request.state.user.get("id")

    try:
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

        post = await db.get(Post, post_id)

        post.bookmark_count = post.bookmark_count + 1

        db.add(post)

        await db.commit()

        return {"detail": "Post was bookmarked successfully"}
    except Exception as e:
        await db.rollback()
        logger.error(f"Post could not be bookmarked: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )

async def unbookmark_post_by_id(db: DBSession, post_id: int, request: Request):
    auth_user_id = request.state.user.get("id")

    try:
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

        post = await db.get(Post, post_id)

        if post.bookmark_count > 0:
            post.bookmark_count = post.bookmark_count - 1

        db.add(post)

        await db.delete(bookmark)
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Post could not be unbookmarked: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )

    return { "detail": "Bookmark removed" }