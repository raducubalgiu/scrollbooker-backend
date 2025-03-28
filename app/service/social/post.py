from fastapi import HTTPException
from starlette.requests import Request
from starlette import status
from sqlalchemy import select, exists
from sqlalchemy.orm import aliased
from app.core.dependencies import DBSession
from app.models import User, Follow
from app.models.social.post_action import post_likes
from app.schema.social.post import PostCreate
from app.models.social.post import Post

async def create_new_post(db: DBSession, new_post: PostCreate, request: Request):
    auth_user_id = request.state.user.get("id")

    if auth_user_id != new_post.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You do not have permission to perform this action')

    post = Post(**new_post.model_dump())
    db.add(post)
    await db.commit()

    return post

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