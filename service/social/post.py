from fastapi import HTTPException
from starlette.requests import Request
from starlette import status
from sqlalchemy import select, exists, desc, func, literal, and_
from sqlalchemy.orm import aliased

from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession, Pagination
from backend.models import User, Follow, PostMedia
from backend.models.social.post_action import post_likes
from backend.schema.social.post import PostCreate, PostResponse, UserPostResponse, PostProduct, PostCounters, LastMinute
from backend.models.social.post import Post
from backend.core.logger import logger
from backend.schema.user.user import UserBaseMinimum


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

async def get_posts_by_user_id(db: DBSession, user_id: int, pagination: Pagination, request: Request):
    auth_user_id = request.state.user.get("id")

    count_stmt = select(func.count()).select_from(Post).where(Post.user_id == user_id)
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
        .join(User, User.id == Post.user_id)
        .join(PostMedia, PostMedia.post_id == Post.id)
        .where(Post.user_id == user_id)
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

async def get_post_likes_by_post_id(db: DBSession, post_id: int, page: int, limit: int, request: Request):
    auth_user_id = request.state.user.get("id")
    f1 = aliased(Follow)

    stmt = await db.execute(
        select(
            User.id,
            User.username,
            User.fullname,
            exists()
            .where((f1.follower_id == auth_user_id) & (f1.followee_id == User.id)) #type: ignore
            .correlate(User)
            .label('is_following')
        )
        .join(post_likes, User.id == post_likes.c.user_id) #type: ignore
        .outerjoin(f1, f1.followee_id == User.id)
        .where(post_likes.c.post_id == post_id)
        .group_by(User.id)
        .limit(limit)
        .offset((page - 1) * limit)
    )

    likes = stmt.mappings().all()
    return likes