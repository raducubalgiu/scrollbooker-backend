from typing import Optional, List

from fastapi import HTTPException, Query
from sqlalchemy.orm import aliased
from starlette.requests import Request
from starlette import status
from sqlalchemy import select, desc, func, literal, and_, or_
from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination, AuthenticatedUser
from models import User, Follow, PostMedia, Repost, BookmarkPost, UserCounters, Like, Business
from schema.social.post import PostCreate, UserPostResponse, PostCounters, LastMinute, PostUserActions, \
    PostBusinessOwner, PostEmployee, PostUser
from models.social.post import Post
from core.logger import logger
from service.social.util.fetch_paginated_posts import fetch_paginated_posts
from service.social.post_media import get_post_media

async def get_explore_feed_posts(
        db: DBSession,
        pagination: Pagination,
        auth_user: AuthenticatedUser,
        business_types: Optional[List[int]] = Query(default=None)
) -> PaginatedResponse[UserPostResponse]:
    auth_user_id = auth_user.id

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
            is_liked.label('is_liked'),
            is_reposted.label('is_reposted'),
            is_bookmarked.label('is_bookmarked'),
            is_followed.label('is_follow'),
        )
        .join(User, User.id == Post.user_id)
        .join(UserCounters, UserCounters.user_id == User.id)

        # Business
        .join(Business, Business.id == Post.business_id)

        # Business Owner
        .join(BusinessOwner, BusinessOwner.id == Post.business_owner_id)
        .join(OwnerCounters, OwnerCounters.user_id == BusinessOwner.id)

        .outerjoin(Employee, Employee.id == Post.employee_id)
    )

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

    for post, u_id, u_fullname, u_username, u_avatar, u_profession, u_ratings_average, u_ratings_count, bo_id, bo_fullname, bo_avatar, bo_ratings_average, e_id, e_fullname, e_avatar, is_liked, is_reposted, is_bookmarked, is_follow in posts:
        media_files = media_map.get(post.id, [])
        employee = PostEmployee(id=e_id, fullname=e_fullname, avatar=e_avatar) if e_id and e_fullname else None

        results.append(UserPostResponse(
            id=post.id,
            description=post.description,
            user=PostUser(
                id=u_id,
                fullname=u_fullname,
                username=u_username,
                avatar=u_avatar,
                profession=u_profession,
                is_follow=is_follow,
                ratings_average=u_ratings_average,
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
            hashtags=post.hashtags,
            bookable=post.bookable,
            rating=post.rating,
            is_video_review=post.is_video_review,
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

async def get_following_posts(
        db: DBSession,
        pagination: Pagination,
        auth_user: AuthenticatedUser
) -> PaginatedResponse[UserPostResponse]:
    auth_user_id = auth_user.id

    base_ids = (
        select(Post.id)
        .join(Follow, and_(
            Follow.followee_id == Post.user_id,
            Follow.follower_id == auth_user_id
        ))
        .distinct()
    )

    return await fetch_paginated_posts(
        db=db,
        auth_user_id=auth_user_id,
        pagination=pagination,
        base_post_ids_query=base_ids
    )

async def get_posts_by_user_id(
        db: DBSession,
        user_id: int,
        pagination: Pagination,
        auth_user: AuthenticatedUser
) -> PaginatedResponse[UserPostResponse]:
    auth_user_id = auth_user.id

    base_ids = (
        select(Post.id)
        .where(Post.user_id == user_id)
    )

    return await fetch_paginated_posts(
        db=db,
        auth_user_id=auth_user_id,
        pagination=pagination,
        base_post_ids_query=base_ids
    )

async def get_video_reviews_by_user_id(
    db: DBSession,
    user_id: int,
    pagination: Pagination,
    auth_user: AuthenticatedUser
) -> PaginatedResponse[UserPostResponse]:
    auth_user_id = auth_user.id

    base_ids = (
        select(Post.id)
        .where(
            Post.is_video_review.is_(True),
            or_(
                Post.employee_id == user_id,
                Post.business_owner_id == user_id
            )
        )
    )

    return await fetch_paginated_posts(
        db=db,
        auth_user_id=auth_user_id,
        pagination=pagination,
        base_post_ids_query=base_ids
    )

async def create_new_post(
        db: DBSession,
        post_create: PostCreate,
        auth_user: AuthenticatedUser
):
    try:
        auth_user_id = auth_user.id

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