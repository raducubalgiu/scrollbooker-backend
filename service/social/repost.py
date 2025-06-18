from fastapi import Request, HTTPException
from starlette import status
from sqlalchemy import select
from backend.core.dependencies import DBSession
from backend.models import Repost, Post
from backend.schema.social.repost import RepostCreate

async def repost_post_by_id(db: DBSession, post_id: int, repost_create: RepostCreate, request: Request):
    auth_user_id = request.state.user.get("id")
    post = await db.get(Post, post_id)

    if auth_user_id == post.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have permission to perform this action"
        )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    stmt = select(Repost).where(
        Repost.user_id == auth_user_id,
        Repost.post_id == post_id
    )

    existing = await db.execute(stmt)

    if existing.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already reposted"
        )

    repost = Repost(
        user_id=auth_user_id,
        post_id=post_id,
        original_poster_id=post.user_id,
        comment=repost_create.comment
    )
    db.add(repost)
    await db.commit()

    return { "detail": "Post was reposted successfully" }

async def unrepost_post_by_id(db: DBSession, post_id: int, request: Request):
    auth_user_id = request.state.user.get("id")

    stmt = select(Repost).where(
        Repost.user_id == auth_user_id,
        Repost.post_id == post_id
    )

    result = await db.execute(stmt)
    repost = result.scalar_one_or_none()

    if not repost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Repost not found"
        )

    await db.delete(repost)
    await db.commit()

    return { "detail": "Repost removed" }