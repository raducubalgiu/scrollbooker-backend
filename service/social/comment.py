from typing import Set, List, Union
from fastapi import HTTPException, Request, Response, status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from schema.social.comment import CommentCreate, CommentResponse, CommentUser
from sqlalchemy import select, update, insert, func, and_, delete
from models import Comment, CommentLike, CommentPostLike, Post, User, UserCounters
from service.social.util.update_post_counter import update_post_counter, PostActionEnum

async def _count_top_level_comments(db: DBSession, post_id: int) -> int:
    top_level_comments = await db.execute(
            select(func.count())
            .select_from(Comment)
            .where(and_(
                Comment.post_id == post_id,
                Comment.parent_id.is_(None)
            ))
        )
    return top_level_comments.scalar_one()

async def _get_user_liked_comment_ids(db: DBSession, user_id: int) -> Set[int]:
    if not user_id:
        return set()

    likes_comment_ids = await db.execute(
        select(CommentLike.comment_id)
        .where(CommentLike.user_id == user_id)
    )
    return set(likes_comment_ids.scalars().all())

async def _get_post_author_id(db: DBSession, post_id: int) -> Union[int, None]:
    return await db.scalar(
        select(Post.user_id)
        .where(Post.id == post_id)
    )

async def _get_post_author_liked_comment_ids(db: DBSession, post_author_id: Union[int, None]) -> Set[int]:
    if not post_author_id:
        return set()
    res = await db.execute(
        select(CommentPostLike.comment_id)
        .where(CommentPostLike.post_author_id == post_author_id)
    )
    return set(res.scalars().all())

async def _select_comments(
    db: DBSession,
    post_id: int,
    page: int,
    limit: int
) -> List[CommentResponse]:
    stmt = (
        select(
        Comment.id,
        Comment.text,
        Comment.post_id,
        Comment.like_count,
        Comment.parent_id,
        Comment.replies_count,
        Comment.created_at,
        User.id.label("user_id"),
        User.username.label("user_username"),
        User.fullname.label("user_fullname"),
        User.avatar.label("user_avatar"),
        User.profession.label("user_profession"),
        UserCounters.ratings_average.label("user_ratings_average"),
    )
    .join(User, User.id == Comment.user_id)
    .join(UserCounters, UserCounters.user_id == Comment.user_id)
    .where(Comment.post_id == post_id, Comment.parent_id.is_(None))
    .offset((page - 1) * limit)
    .limit(limit)
    .order_by(Comment.created_at.asc()))

    rows = await db.execute(stmt)
    return rows.fetchall()

async def _count_replies(
        db: DBSession,
        parent_id: int
) -> int:
    count_replies = await db.execute(
        select(func.count())
        .select_from(Comment)
        .where(Comment.parent_id == parent_id)
    )
    return count_replies.scalar_one()

async def _select_replies(
    db: DBSession,
    post_id: int,
    parent_id: int,
    page: int, limit: int
) -> List[CommentResponse]:
    replies = await db.execute(
        select(
            Comment.id,
            Comment.text,
            Comment.post_id,
            Comment.like_count,
            Comment.parent_id,
            Comment.replies_count,
            Comment.created_at,
            User.id.label("user_id"),
            User.username.label("user_username"),
            User.fullname.label("user_fullname"),
            User.avatar.label("user_avatar"),
            User.profession.label("user_profession"),
            UserCounters.ratings_average.label("user_ratings_average"),
        )
        .join(User, User.id == Comment.user_id)
        .join(UserCounters, UserCounters.user_id == Comment.user_id)
        .where(
            Comment.post_id == post_id,
            Comment.parent_id == parent_id
        )
        .offset((page - 1) * limit)
        .limit(limit)
        .order_by(Comment.created_at.asc())
    )

    return replies.fetchall()

async def create_new_comment(
        db: DBSession,
        post_id: int,
        comment_data: CommentCreate,
        request: Request
) -> CommentResponse:
    async with db.begin():
        auth_user_id = request.state.user.get("id")

        if await _get_post_author_id(db, post_id) is None:
            raise HTTPException(status_code=404, detail="Post not found")

        if comment_data.parent_id is not None:
            parent_ok = await db.scalar(
                select(func.count()).select_from(Comment)
                .where(Comment.id == comment_data.parent_id, Comment.post_id == post_id)
            )

            if not parent_ok:
                raise HTTPException(status_code=422, detail="Invalid parent comment")

        new_comment = Comment(
            **comment_data.model_dump(),
            post_id=post_id,
            user_id=auth_user_id,
        )
        db.add(new_comment)

        if comment_data.parent_id is None:
            await update_post_counter(db, model=Comment, post_id=post_id, action=PostActionEnum.ADD)

        await db.flush()
        await db.refresh(new_comment, attribute_names=["id", "created_at", "like_count", "parent_id", "text", "post_id"])

        comment_user = await db.execute(
            select(User.id, User.username, User.fullname, User.avatar)
            .where(User.id == auth_user_id)
        )
        user = comment_user.fetchone()

        return CommentResponse(
            id=new_comment.id,
            text=new_comment.text,
            user=CommentUser(
                id=user.id,
                username=user.username,
                fullname=user.fullname,
                avatar=user.avatar,
            ),
            replies_count=0,
            post_id=new_comment.post_id,
            like_count=new_comment.like_count,
            is_liked=False,
            liked_by_post_author=False,
            parent_id=new_comment.parent_id,
            created_at=new_comment.created_at,
        )

async def get_comments_by_post_id(
        db: DBSession,
        post_id: int,
        pagination: Pagination,
        request: Request
) -> PaginatedResponse[CommentResponse]:
    auth_user_id = request.state.user.get("id")

    count = await _count_top_level_comments(db, post_id)
    comments = await _select_comments(db, post_id, pagination.page, pagination.limit)

    user_liked_comments = await _get_user_liked_comment_ids(db, auth_user_id)
    post_author_id = await _get_post_author_id(db, post_id)
    post_author_liked_comments = await _get_post_author_liked_comment_ids(db, post_author_id)

    results = [
        CommentResponse(
            id=comment.id,
            text=comment.text,
            user=CommentUser(
                id=comment.user_id,
                username=comment.user_username,
                fullname=comment.user_fullname,
                avatar=comment.user_avatar
            ),
            post_id=comment.post_id,
            replies_count=comment.replies_count,
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

async def get_comments_by_parent_id(
    db: DBSession,
    post_id: int,
    parent_id: int,
    pagination: Pagination,
    request: Request,
    ) -> PaginatedResponse[CommentResponse]:
        auth_user_id = request.state.user.get("id")

        parent_info = await db.execute(
            select(Comment.id, Comment.post_id)
            .where(Comment.id == parent_id)
            )
        parent = parent_info.fetchone()

        if parent is None:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        if parent.post_id != post_id:
            raise HTTPException(status_code=422, detail="Parent comment does not belong to this post")

        count = await _count_replies(db, parent_id)
        rows = await _select_replies(db, post_id, parent_id, pagination.page, pagination.limit)

        user_liked_comments = await _get_user_liked_comment_ids(db, auth_user_id)
        post_author_id = await _get_post_author_id(db, post_id)
        post_author_liked_comments = await _get_post_author_liked_comment_ids(db, post_author_id)

        results = [
            CommentResponse(
                id=r.id,
                text=r.text,
                user=CommentUser(
                    id=r.user_id,
                    username=r.user_username,
                    fullname=r.user_fullname,
                    avatar=r.user_avatar,
                ),
                post_id=r.post_id,
                replies_count=r.replies_count,
                like_count=r.like_count,
                is_liked=r.id in user_liked_comments,
                liked_by_post_author=r.id in post_author_liked_comments,
                parent_id=r.parent_id,
                created_at=r.created_at,
            ) for r in rows
        ]

        return PaginatedResponse(count=count, results=results)

async def like_post_comment(
        db: DBSession,
        comment_id: int,
        request: Request
) -> Response:
    auth_user_id = request.state.user.get("id")

    async with db.begin():
        comment = await db.get(Comment, comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Comment not found')

        post = await db.get(Post, comment.post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Post not found')

        is_post_author = auth_user_id == post.user_id

        is_liked = await db.execute(
            select(CommentLike)
            .where(and_(
                CommentLike.comment_id == comment_id,
                CommentLike.user_id == auth_user_id
            ))
        )

        if is_liked.scalar():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Comment already liked')

        await db.execute(
            insert(CommentLike)
            .values(
                comment_id=comment_id,
                user_id=auth_user_id
            )
        )

        await db.execute(
            update(Comment)
            .where(Comment.id == comment_id)
            .values(like_count=Comment.like_count + 1)
        )

        if is_post_author:
            await db.execute(
                insert(CommentPostLike)
                .values(
                    comment_id=comment_id,
                    post_author_id=auth_user_id
                )
            )

        return Response(status_code=status.HTTP_201_CREATED)

async def unlike_post_comment(
        db: DBSession,
        comment_id: int,
        request: Request
) -> Response:
    auth_user_id = request.state.user.get("id")

    async with db.begin():
        comment = await db.get(Comment, comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Comment not found')

        post = await db.get(Post, comment.post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Post not found')

        is_post_author = auth_user_id == post.user_id

        query = await db.execute(
            select(CommentLike)
            .where(and_(
                CommentLike.comment_id == comment_id,
                CommentLike.user_id == auth_user_id
            ))
        )
        liked = query.scalar()

        if not liked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Comment not liked')

        await db.execute(
            delete(CommentLike)
            .where(and_(
                CommentLike.comment_id == comment_id,
                CommentLike.user_id== auth_user_id
            ))
        )

        await db.execute(
            update(Comment)
            .where(Comment.id == comment_id)
            .values(like_count=Comment.like_count - 1)
        )

        if is_post_author:
            await db.execute(
                delete(CommentPostLike)
                .where(and_(
                    CommentPostLike.comment_id == comment_id,
                    CommentPostLike.post_author_id == auth_user_id
                ))
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

