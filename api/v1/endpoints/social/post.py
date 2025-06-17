from typing import Union

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession, Pagination
from backend.core.enums.enums import PostAction
from backend.schema.social.post import PostResponse, PostCreate, UserPostResponse
from backend.schema.social.comment import CommentCreate, CommentBase
from backend.service.social.post import create_new_post, get_post_likes_by_post_id, get_posts_by_user_id
from backend.service.social.post_action import check_post_action, perform_post_action, remove_post_action
from backend.service.social.comment import create_new_comment, like_post_comment, unlike_post_comment, get_comments_by_post_id

router = APIRouter(tags=["Posts"])

@router.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(db: DBSession, post_create: PostCreate, request: Request):
    return await create_new_post(db, post_create, request)

@router.get("/users/{user_id}/posts",
            summary='List All Posts By User Id',
            response_model=PaginatedResponse[UserPostResponse])
async def get_posts_by_user(db: DBSession, user_id: int, pagination: Pagination, request: Request):
    return await get_posts_by_user_id(db, user_id, pagination, request)

@router.get("/posts/{post_id}/likes")
async def get_post_likes(db: DBSession, post_id: int, page: int, limit: int, request: Request):
    return await get_post_likes_by_post_id(db, post_id, page, limit, request)

# LIKES
@router.get("/posts/{post_id}/likes/check", response_model=bool)
async def check_like(db: DBSession, post_id: int, request: Request):
    return await check_post_action(db, post_id, request, action=PostAction.LIKE)

@router.post("/posts/{post_id}/likes", status_code=status.HTTP_201_CREATED)
async def like(db: DBSession, post_id: int, request: Request):
    return await perform_post_action(db, post_id, request, action=PostAction.LIKE)

@router.delete("/posts/{post_id}/likes", status_code=status.HTTP_204_NO_CONTENT)
async def unlike(db: DBSession, post_id: int, request: Request):
    return await remove_post_action(db, post_id, request, action=PostAction.LIKE)

# SAVES
@router.get("/posts/{post_id}/saves/check", response_model=bool)
async def check_save(db: DBSession, post_id: int, request: Request):
    return await check_post_action(db, post_id, request, action=PostAction.SAVE)

@router.post("/posts/{post_id}/saves", status_code=status.HTTP_201_CREATED)
async def save(db: DBSession, post_id: int, request: Request):
    return await perform_post_action(db, post_id, request, action=PostAction.SAVE)

@router.delete("/posts/{post_id}/saves", status_code=status.HTTP_204_NO_CONTENT)
async def unsave(db: DBSession, post_id: int, request: Request):
    return await remove_post_action(db, post_id, request, action=PostAction.SAVE)

# SHARES
@router.get("/posts/{post_id}/shares/check", response_model=bool)
async def check_share(db: DBSession, post_id: int, request: Request):
    return await check_post_action(db, post_id, request, action=PostAction.SHARE)

@router.post("/posts/{post_id}/shares", status_code=status.HTTP_201_CREATED)
async def share(db: DBSession, post_id: int, request: Request):
    return await perform_post_action(db, post_id, request, action=PostAction.SHARE)

@router.delete("/posts/{post_id}/shares", status_code=status.HTTP_204_NO_CONTENT)
async def unshare(db: DBSession, post_id: int, request: Request):
    return await remove_post_action(db, post_id, request, action=PostAction.SHARE)

# COMMENTS
@router.get("/posts/{post_id}/comments")
async def get_comments(db: DBSession, post_id: int, page: int, limit: int, request: Request):
    return await get_comments_by_post_id(db, post_id, page, limit, request)

@router.post("/posts/{post_id}/comments", response_model=CommentBase)
async def create_comment(db: DBSession, post_id: int, comment_data: CommentCreate, request: Request):
    return await create_new_comment(db, post_id, comment_data, request)

@router.post("/posts/{post_id}/comments/{comment_id}/like", status_code=status.HTTP_201_CREATED)
async def like_comment(db: DBSession, post_id: int, comment_id: int, request: Request):
    return await like_post_comment(db, post_id, comment_id, request)

@router.delete("/posts/{post_id}/comments/{comment_id}/unlike", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_comment(db: DBSession, post_id: int, comment_id: int, request: Request):
    return await unlike_post_comment(db, post_id, comment_id, request)
