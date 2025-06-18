from operator import and_

from fastapi import HTTPException
from starlette.requests import Request
from starlette import status
from sqlalchemy import select, func, literal, desc

from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession, Pagination
from backend.models import BookmarkPost, Post, Follow, User, PostMedia
from backend.schema.social.post import UserPostResponse, PostProduct, PostCounters, LastMinute
from backend.schema.user.user import UserBaseMinimum


async def get_bookmarked_posts_by_user(db: DBSession, request: Request, pagination: Pagination):
    auth_user_id = request.state.user.get("id")

    count_stmt = select(func.count()).select_from(BookmarkPost).where(BookmarkPost.user_id == auth_user_id)
    count_total = await db.execute(count_stmt)
    count = count_total.scalar_one()

    is_follow_subq = (
        select(literal(True))
        .select_from(Follow)
        .where(and_(
            Follow.follower_id == auth_user_id,
            Follow.followee_id == User.id)
        )
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
            is_follow_subq.label("is_follow")
        )
        .join(BookmarkPost, BookmarkPost.post_id == Post.id)
        .join(User, User.id == Post.user_id)
        .outerjoin(PostMedia, PostMedia.post_id == Post.id)
        .where(BookmarkPost.user_id == auth_user_id)
        .order_by(desc(Post.created_at))
        .offset(
            (pagination.page - 1) * pagination.limit
        )
        .limit(pagination.limit)
    )
    posts = result.all()

    results = []

    for post, u_id, u_fullname, u_username, u_avatar, u_profession, is_follow in posts:
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
                save_count=post.save_count,
                share_count=post.share_count
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