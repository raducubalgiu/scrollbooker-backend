from typing import Tuple

from sqlalchemy import select, literal, and_, func, desc, or_
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Select
from core.crud_helpers import PaginatedResponse
from core.dependencies import Pagination, DBSession
from models import Like, Post, Repost, BookmarkPost, Follow, User, UserCounters, Product, Currency, Business
from schema.social.post import UserPostResponse, PostProduct, PostProductCurrency, PostCounters, PostUserActions, \
    LastMinute, PostBusinessOwner, PostEmployee, PostUser
from service.social.post_media import get_post_media

def build_posts_list_query(
        auth_user_id: int,
        pagination: Pagination,
        base_post_ids_query: Select
) -> Tuple[Select, Select]:
    ids_sq = base_post_ids_query.subquery()

    BusinessOwner = aliased(User)
    OwnerCounters = aliased(UserCounters)
    Employee = aliased(User)

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

    is_followed = (
        select(literal(True))
        .select_from(Follow)
        .where(and_(
            Follow.follower_id == auth_user_id,
            Follow.followee_id == User.id)
        )
        .correlate(User)
        .exists()
    )

    count_query = select(func.count()).select_from(ids_sq)

    list_query = (
        select(
            Post,
            User.id, User.fullname, User.username, User.avatar, User.profession,
            UserCounters.ratings_average,
            UserCounters.ratings_count,
            BusinessOwner.id.label('bo_id'),
            BusinessOwner.fullname.label('bo_fullname'),
            BusinessOwner.avatar.label("bo_avatar"),
            OwnerCounters.ratings_average.label("bo_ratings_average"),
            Employee.id.label('e_id'),
            Employee.fullname.label('e_fullname'),
            Employee.avatar.label("e_avatar"),
            Product,
            Currency,
            is_liked.label('is_liked'),
            is_reposted.label('is_reposted'),
            is_bookmarked.label('is_bookmarked'),
            is_followed.label('is_follow'),
        )
        .join(ids_sq, ids_sq.c.id == Post.id)
        .join(User, User.id == Post.user_id)
        .join(UserCounters, UserCounters.user_id == User.id)

        # Business
        .join(Business, Business.id == Post.business_id)

        # Business Owner
        .join(BusinessOwner, BusinessOwner.id == Post.business_owner_id)
        .join(OwnerCounters, OwnerCounters.user_id == BusinessOwner.id)

        # Employee
        .outerjoin(Employee, Employee.id == Post.employee_id)

        .outerjoin(Product, Product.id == Post.product_id)
        .outerjoin(Currency, Currency.id == Product.currency_id)

        .order_by(desc(Post.created_at))
        .offset((pagination.page - 1) * pagination.limit)
        .limit(pagination.limit)
    )
    return count_query, list_query

def row_to_response(row, media_map) -> UserPostResponse:
    (
         post,
         u_id, u_fullname, u_username, u_avatar, u_profession, u_ratings_avg, u_ratings_count,
         bo_id, bo_fullname, bo_avatar, bo_ratings_average,
         e_id, e_fullname, e_avatar,
         product,
         currency,
         is_liked,
         is_reposted,
         is_bookmarked,
         is_follow
    ) = row
    media_files = media_map.get(post.id, [])

    employee = PostEmployee(id=e_id, fullname=e_fullname, avatar=e_avatar) if e_id and e_fullname else None

    return UserPostResponse(
        id=post.id,
        description=post.description,
        user=PostUser(
            id=u_id,
            fullname=u_fullname,
            username=u_username,
            avatar=u_avatar,
            profession=u_profession,
            is_follow=is_follow,
            ratings_average=u_ratings_avg,
            ratings_count=u_ratings_count
        ),
        business_owner=PostBusinessOwner(
            id=bo_id,
            fullname=bo_fullname,
            avatar=bo_avatar,
            ratings_average=bo_ratings_average
        ),
        employee=employee,
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
            bookings_count=post.bookings_count,
        ),
        media_files=media_files,
        user_actions=PostUserActions(
            is_liked=is_liked,
            is_bookmarked=is_bookmarked,
            is_reposted=is_reposted,
        ),
        mentions=post.mentions,
        hashtags=post.hashtags,
        is_video_review=post.is_video_review,
        rating=post.rating,
        bookable=post.bookable,
        last_minute=LastMinute(
            is_last_minute=post.is_last_minute,
            last_minute_end=post.last_minute_end,
            has_fixed_slots=post.has_fixed_slots,
            fixed_slots=post.fixed_slots
        ),
        created_at=post.created_at
    )

async def fetch_paginated_posts(
        db: DBSession,
        auth_user_id: int,
        pagination: Pagination,
        base_post_ids_query: Select
    ) -> PaginatedResponse[UserPostResponse]:
    count_q, list_q = build_posts_list_query(auth_user_id, pagination, base_post_ids_query)

    count = (await db.execute(count_q)).scalar_one()

    rows = (await db.execute(list_q)).all()
    post_ids = [post.id for (post, *_) in rows]
    media_map = await get_post_media(db, post_ids)

    results = [row_to_response(row, media_map) for row in rows]
    return PaginatedResponse(count=count, results=results)