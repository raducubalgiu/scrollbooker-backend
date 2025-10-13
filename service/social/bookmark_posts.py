from enum import Enum

from fastapi import HTTPException, Request, status, Response
from sqlalchemy import select, func, literal, desc, and_, insert, update, delete

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from models import BookmarkPost, Post, Follow, User, Repost, Product
from schema.social.post import UserPostResponse, PostCounters, LastMinute, PostUserActions
from schema.user.user import UserBaseMinimum
from service.social.post_media import get_post_media
from core.logger import logger

class BookmarkTypeEnum(str, Enum):
    BOOKMARK = "BOOKMARK"
    UNBOOKMARK = "UNBOOKMARK"

async def _is_post_bookmarked(db: DBSession, post_id: int, auth_user_id: int) -> bool:
    existing = await db.execute(
        select(BookmarkPost).where(
            and_(
                BookmarkPost.user_id == auth_user_id,
                BookmarkPost.post_id == post_id
            )
        )
    )
    return True if existing.scalar() else False

async def _update_post_bookmark_counter(db: DBSession, post_id: int, action_type: BookmarkTypeEnum) -> None:
    delta = 1 if action_type == BookmarkTypeEnum.BOOKMARK else -1

    await db.execute(
        update(Post)
        .where(Post.id == post_id)
        .values(bookmark_count=func.greatest(Post.bookmark_count + delta, 0))
    )

async def get_bookmarked_posts_by_user(db: DBSession, user_id: int, pagination: Pagination):
    count_stmt = select(func.count()).select_from(BookmarkPost).where(and_(BookmarkPost.user_id == user_id))
    count_total = await db.execute(count_stmt)
    count = count_total.scalar_one()

    is_reposted = (
        select(literal(True))
        .select_from(Repost)
        .where(and_(
            Repost.user_id == user_id,
            Repost.post_id == Post.id)
        )
        .correlate(Post)
        .exists()
    )

    is_bookmarked = (
        select(literal(True))
        .select_from(BookmarkPost)
        .where(and_(
            BookmarkPost.user_id == user_id,
            BookmarkPost.post_id == Post.id)
        )
        .correlate(Post)
        .exists()
    )

    is_follow = (
        select(literal(True))
        .select_from(Follow)
        .where(and_(
            Follow.follower_id == user_id,
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
            Product,
            is_follow,
            is_bookmarked,
            is_reposted,
        )
        .join(User, User.id == Post.user_id)
        .join(BookmarkPost, BookmarkPost.user_id == user_id)
        .join(Product, Product.user_id == Post.user_id)
        .where(BookmarkPost.post_id == Post.id)
        .order_by(desc(Post.created_at))
        .offset((pagination.page - 1) * pagination.limit)
        .limit(pagination.limit)
    )
    posts = result.all()

    post_ids = [p.id for p, *_ in posts]
    media_map = await get_post_media(db, post_ids)

    results = []

    for post, u_id, u_fullname, u_username, u_avatar, u_profession, product, is_follow, is_reposted, is_bookmarked in posts:
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
            product=product,
            counters=PostCounters(
                comment_count=post.comment_count,
                like_count=post.like_count,
                bookmark_count=post.bookmark_count,
                share_count=post.share_count,
                bookings_count=post.bookings_count
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

async def bookmark_post_by_id(db: DBSession, post_id: int, request: Request) -> Response:
    auth_user_id = request.state.user.get("id")

    try:
        async with db.begin():
            if await _is_post_bookmarked(db, post_id, auth_user_id):
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
            if not await _is_post_bookmarked(db, post_id, auth_user_id):
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