from typing import Optional, List

from fastapi import HTTPException, Query
from starlette.requests import Request
from starlette import status
from sqlalchemy import select, desc, func, literal, and_
from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from models import User, Follow, PostMedia, Repost, BookmarkPost, UserCounters, Like, Product, Currency
from schema.social.post import PostCreate, UserPostResponse, PostCounters, LastMinute, PostUserActions, PostProduct, \
    PostProductCurrency
from models.social.post import Post
from core.logger import logger
from schema.user.user import UserBaseMinimum
from service.social.post_media import get_post_media

async def get_explore_feed_posts(
        db: DBSession,
        pagination: Pagination,
        request: Request,
        business_types: Optional[List[int]] = Query(default=None)
):
    auth_user_id = request.state.user.get("id")

    is_liked = (
        select(literal(True))
        .select_from(Like)
        .where(and_(
            Like.user_id == auth_user_id,
            Like.post_id == Post.id)
        )
        .correlate(Post)
        .exists()
    )

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

    base_query = (
        select(Post.id)
        .join(User, User.id == Post.user_id)
    )

    if business_types:
        base_query = base_query.where(Post.business_type_id.in_(business_types))

    count_query = select(func.count()).select_from(base_query.subquery())
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
        .outerjoin(Product, Product.id == Post.product_id)
        .outerjoin(Currency, Currency.id == Product.currency_id)
        .join(UserCounters, UserCounters.user_id == User.id))

    if business_types:
        query = query.where(Post.business_type_id.in_(business_types))

    query = (
        query
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

async def get_following_posts(db: DBSession, pagination: Pagination, request: Request):
    auth_user_id = request.state.user.get("id")

    is_liked = (
        select(literal(True))
        .select_from(Like)
        .where(and_(
            Like.user_id == auth_user_id,
            Like.post_id == Post.id)
        )
        .correlate(Post)
        .exists()
    )

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

    base_count_query = (
        select(Post.id)
        .join(User, User.id == Post.user_id)
        .join(Follow, Follow.followee_id == User.id)
        .where(Follow.follower_id == auth_user_id)
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
            is_reposted,
            is_bookmarked
        )
        .join(User, User.id == Post.user_id)
        .join(Follow, Follow.followee_id == User.id)
        .outerjoin(Product, Product.id == Post.product_id)
        .outerjoin(Currency, Currency.id == Product.currency_id)
        .join(UserCounters, UserCounters.user_id == User.id)
        .where(Follow.follower_id == auth_user_id)
        .order_by(desc(Post.created_at))
        .offset((pagination.page - 1) * pagination.limit)
        .limit(pagination.limit)
    )

    posts_result = await db.execute(query)
    posts = posts_result.all()

    post_ids = [p.id for p, *_ in posts]
    media_map = await get_post_media(db, post_ids)

    results = []

    for post, u_id, u_fullname, u_username, u_avatar, u_profession, u_ratings_average, product, currency, is_liked, is_reposted, is_bookmarked in posts:
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
                is_follow=True,
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

async def get_posts_by_user_id(db: DBSession, user_id: int, pagination: Pagination, request: Request):
    auth_user_id = request.state.user.get("id")

    count_stmt = select(func.count()).select_from(Post).where(Post.user_id == user_id)
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
            Product,
            Currency,
            is_follow,
            is_reposted,
            is_bookmarked
        )
        .join(User, User.id == Post.user_id)
        .outerjoin(Product, Product.id == Post.product_id)
        .outerjoin(Currency, Currency.id == Product.currency_id)
        .where(Post.user_id == user_id)
        .order_by(desc(Post.created_at))
        .offset((pagination.page - 1) * pagination.limit)
        .limit(pagination.limit)
    )
    posts = result.all()

    post_ids = [p.id for p, *_ in posts]
    media_map = await get_post_media(db, post_ids)

    results = []

    for post, u_id, u_fullname, u_username, u_avatar, u_profession, product, currency, is_follow, is_reposted, is_bookmarked in posts:
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

async def create_new_post(db: DBSession, post_create: PostCreate, request: Request):
    auth_user_id = request.state.user.get("id")

    try:
        post_data = post_create.model_dump(exclude={"media_files"})
        post_data["user_id"] = auth_user_id

        post = Post(**post_data)
        db.add(post)

        await db.flush()

        media_files = []

        for i, media_file in enumerate(post_create.media_files):
            media_files.append(
                PostMedia(
                    url=media_file.url,
                    type=media_file.type,
                    thumbnail_url=media_file.thumbnail_url,
                    duration=media_file.duration,
                    post_id=post.id,
                    order_index=i
                )
            )

        db.add_all(media_files)

        await db.commit()

        return { "detail": "Post Created Successfully" }

    except Exception as e:
        await db.rollback()
        logger.error(f"Post could not be created. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )