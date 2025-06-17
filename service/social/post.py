from fastapi import HTTPException
from starlette.requests import Request
from starlette import status
from sqlalchemy import select, exists
from sqlalchemy.orm import aliased
from backend.core.dependencies import DBSession
from backend.models import User, Follow, PostMedia
from backend.models.social.post_action import post_likes
from backend.schema.social.post import PostCreate
from backend.models.social.post import Post
from backend.core.logger import logger

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