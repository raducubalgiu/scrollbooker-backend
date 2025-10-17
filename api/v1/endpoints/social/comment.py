from fastapi import APIRouter
from starlette.requests import Request
from starlette import status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from schema.social.comment import CommentCreate, CommentResponse
from service.social.comment import get_comments_by_post_id, create_new_comment, like_post_comment, \
    unlike_post_comment, get_comments_by_parent_id

router = APIRouter(tags=["Comments"])

@router.get("/posts/{post_id}/comments",
            summary='List All Comments By Post Id',
            response_model=PaginatedResponse[CommentResponse])
async def get_comments(db: DBSession, post_id: int, pagination: Pagination, request: Request):
    return await get_comments_by_post_id(db, post_id, pagination, request)

@router.get("/posts/{post_id}/comments/{parent_id}/replies",
            summary='List All Comment Replies',
            response_model=PaginatedResponse[CommentResponse])
async def get_comment_replies(db: DBSession, post_id: int, parent_id: int, pagination: Pagination, request: Request):
    return await get_comments_by_parent_id(db, post_id, parent_id, pagination, request)

@router.post("/posts/{post_id}/comments",
             summary='Create New Comment',
             response_model=CommentResponse)
async def create_comment(db: DBSession, post_id: int, comment_data: CommentCreate, request: Request):
    return await create_new_comment(db, post_id, comment_data, request)

@router.post("/comments/{comment_id}/likes",
             summary='Like Comment',
             status_code=status.HTTP_201_CREATED)
async def like_comment(db: DBSession, comment_id: int, request: Request):
    return await like_post_comment(db, comment_id, request)

@router.delete("/comments/{comment_id}/likes",
               summary='Unlike Comment',
               status_code=status.HTTP_204_NO_CONTENT)
async def unlike_comment(db: DBSession, comment_id: int, request: Request):
    return await unlike_post_comment(db, comment_id, request)