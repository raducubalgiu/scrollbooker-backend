from enum import Enum

from fastapi import HTTPException, Request, status, Response
from sqlalchemy import select, func, literal, and_, desc, update, insert, delete

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from models import User, Follow, Repost, BookmarkPost, Product, Like, Currency, UserCounters
from schema.social.post import UserPostResponse, PostCounters, \
    LastMinute, PostUserActions, PostProduct, PostProductCurrency
from models.social.post import Post
from schema.social.repost import RepostCreate
from schema.user.user import UserBaseMinimum
from service.social.post_media import get_post_media
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

async def get_reposts_by_user(db: DBSession, user_id: int, pagination: Pagination):
    # count_stmt = select(func.count()).select_from(Repost).where(and_(Repost.user_id == user_id))
    # count_total = await db.execute(count_stmt)
    # count = count_total.scalar_one()

    is_liked = (
        select(literal(True))
        .select_from(Like)
        .where(and_(
            Like.user_id == user_id,
            Like.post_id == Post.id)
        )
        .correlate(Post)
        .exists()
    )

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

    base_count_query = (
        select(Post.id)
        .join(User, User.id == Post.user_id)
        .join(Repost, Repost.post_id == Post.id)
        .where(and_(
            Repost.user_id == user_id,
            Repost.post_id == Post.id
        ))
    )

    count_query = select(func.count()).select_from(base_count_query.subquery())
    count_total = await db.execute(count_query)
    count = count_total.scalar_one()

    query = (
        select(
            Post,
            User.id,
            User.fullname,
            User.username,
            User.avatar,
            User.profession,
            UserCounters.ratings_average,
            Product,
            Currency,
            is_liked,
            is_follow,
            is_reposted,
            is_bookmarked
        )
        .join(User, User.id == Post.user_id)
        .join(BookmarkPost, BookmarkPost.post_id == Post.id)
        .outerjoin(Product, Product.id == Post.product_id)
        .outerjoin(Currency, Currency.id == Product.currency_id)
        .join(UserCounters, UserCounters.user_id == User.id)

        .where(and_(
            Repost.user_id == user_id,
            Repost.post_id == Post.id
        ))
        .order_by(desc(Post.created_at))
        .offset((pagination.page - 1) * pagination.limit)
        .limit(pagination.limit)
    )

    posts_result = await db.execute(query)
    posts = posts_result.all()

    post_ids = [p.id for p, *_ in posts]
    media_map = await get_post_media(db, post_ids)

    results = []

    for post, u_id, u_fullname, u_username, u_avatar, u_profession, u_ratings_average, product, currency, is_liked, is_follow, is_reposted, is_bookmarked in posts:
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
                is_follow=is_follow,
                ratings_average=u_ratings_average,
            ),
            business_id=post.business_id,
            product=PostProduct(
                id=product.id,
                name=product.name,
                description=product.description,
                duration=product.duration,
                price=product.price,
                price_with_discount=product.price_with_discount,
                discount=product.discount,
                currency=PostProductCurrency(
                    id=currency.id,
                    name=currency.name
                )
            ) if product is not None else None,
            counters=PostCounters(
                comment_count=post.comment_count,
                like_count=post.like_count,
                bookmark_count=post.bookmark_count,
                repost_count=post.repost_count,
                bookings_count=post.bookings_count
            ),
            media_files=media_files,
            user_actions=PostUserActions(
                is_liked=is_liked,
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