from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from starlette.requests import Request
from starlette import status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from schema.social.comment import CommentCreate, CommentResponse
from sqlalchemy import select, update, insert, func
from models import Comment, CommentLike, CommentPostLike, Post, User, Review
from core.logger import logger

async def create_new_comment(db: DBSession, post_id: int, comment_data: CommentCreate, request: Request):
    auth_user_id = request.state.user.get("id")
    new_comment = Comment(**comment_data.model_dump(), post_id=post_id, user_id=auth_user_id)

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


async def like_post_comment(db: DBSession, post_id: int, comment_id: int, request: Request):
    auth_user_id = request.state.user.get("id")
    comment = await db.get(Comment, comment_id)
    post = await db.get(Post, post_id)

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Comment not found')
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Post not found')

    is_post_author = auth_user_id == post.user_id

    query = await db.execute(
        select(CommentLike)
        .where((CommentLike.comment_id == comment_id) & (CommentLike.user_id == auth_user_id))  # type: ignore
    )
    liked = query.scalar()

    if liked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Comment already liked')
    try:
        await db.execute(insert(CommentLike).values(comment_id=comment_id, user_id=auth_user_id))
        await db.execute(
            update(Comment)
            .where(Comment.id == comment_id) #type: ignore
            .values(like_count=Comment.like_count + 1)
        )
        if is_post_author:
            await db.execute(
                insert(CommentPostLike)
                .values(comment_id=comment_id, post_author_id=auth_user_id)
            )

        await db.commit()
        return {"detail": "Comment liked!"}
    except Exception as e:
        await db.rollback()
        logger.error(f"Comment could not be liked. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')

async def unlike_post_comment(db: DBSession, post_id: int, comment_id: int, request: Request):
    auth_user_id = request.state.user.get("id")
    comment = await db.get(Comment, comment_id)
    post = await db.get(Post, post_id)

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Comment not found')
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Post not found')

    is_post_author = auth_user_id == post.user_id

    query = await db.execute(
        select(CommentLike)
        .where((CommentLike.comment_id == comment_id) & (CommentLike.user_id == auth_user_id))  # type: ignore
    )
    liked = query.scalar()

    if not liked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Comment not liked')
    try:
        await db.delete(liked)
        await db.execute(
            update(Comment)
            .where(Comment.id == comment_id)  # type: ignore
            .values(like_count=Comment.like_count - 1)
        )

        if is_post_author:
            query = await db.execute(
                select(CommentPostLike)
                .where(
                    (CommentPostLike.comment_id == comment_id) & (CommentPostLike.post_author_id == auth_user_id)) #type: ignore
            )
            comment_post_like = query.scalar()
            await db.delete(comment_post_like)

        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Comment could not be unliked. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')

async def get_comments_by_post_id(db: DBSession, post_id: int, pagination: Pagination, request: Request):
    auth_user_id = request.state.user.get("id")

    count_stmt = (select(func.count())
        .select_from(Comment)
        .where(
            Comment.post_id == post_id,
            Comment.parent_id.is_(None)
        ))
    count_total = await db.execute(count_stmt)
    count = count_total.scalar_one()

    query = await db.execute(
        select(Comment)
        .where(
            Comment.post_id == post_id,
            Comment.parent_id.is_(None)
        )
        .options(
            joinedload(Comment.user).load_only(
                User.id,
                User.username,
                User.fullname,
                User.avatar,
                User.profession
            )
        )
        .offset((pagination.page - 1) * pagination.limit)
        .limit(pagination.limit)
        .order_by(Comment.created_at.asc())
    )
    comments = query.scalars().all()

    # Get likes by the authenticated user
    user_likes_query = await db.execute(
        select(CommentLike.comment_id)
        .where(CommentLike.user_id == auth_user_id) # type: ignore
    )
    user_liked_comments = user_likes_query.scalars().all()

    # Get post author likes
    post_author_query = await db.execute(
        select(Post.user_id)
        .where(Post.id == post_id) #type: ignore
    )
    post_author_id = post_author_query.scalar()

    post_author_likes = await db.execute(
        select(CommentPostLike.comment_id)
        .where(CommentPostLike.post_author_id == post_author_id) #type: ignore
    )
    post_author_liked_comments = post_author_likes.scalars().all()

    results = [
        CommentResponse(
            id=comment.id,
            text=comment.text,
            user=comment.user,
            post_id=comment.post_id,
            like_count=comment.like_count,
            is_liked=comment.id in user_liked_comments,
            liked_by_post_author=comment.id in post_author_liked_comments,
            parent_id=comment.parent_id,
            created_at=comment.created_at
        ) for comment in comments
    ]

    return PaginatedResponse(
        count=count,
        results=results
    )
