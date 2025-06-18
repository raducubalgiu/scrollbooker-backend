from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession, Pagination
from backend.schema.social.post import PostCreate, UserPostResponse
from backend.schema.social.comment import CommentCreate, CommentBase
from backend.service.social.post import create_new_post, get_posts_by_user_id
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

# # SHARES
# @router.get("/posts/{post_id}/shares/check", response_model=bool)
# async def check_share(db: DBSession, post_id: int, request: Request):
#     return await check_post_action(db, post_id, request, action=PostAction.SHARE)
#
# @router.post("/posts/{post_id}/shares", status_code=status.HTTP_201_CREATED)
# async def share(db: DBSession, post_id: int, request: Request):
#     return await perform_post_action(db, post_id, request, action=PostAction.SHARE)
#
# @router.delete("/posts/{post_id}/shares", status_code=status.HTTP_204_NO_CONTENT)
# async def unshare(db: DBSession, post_id: int, request: Request):
#     return await remove_post_action(db, post_id, request, action=PostAction.SHARE)

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
