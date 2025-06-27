from fastapi import APIRouter
from starlette.requests import Request
from starlette import status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from schema.social.comment import CommentCreate, CommentResponse
from service.social.comment import get_comments_by_post_id, create_new_comment, like_post_comment, \
    unlike_post_comment

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["Comments"])

@router.get("/",
            summary='List All Comments By Post Id',
            response_model=PaginatedResponse[CommentResponse])
async def get_comments(db: DBSession, post_id: int, pagination: Pagination, request: Request):
    return await get_comments_by_post_id(db, post_id, pagination, request)

@router.post("/",
             summary='Create New Comment',
             status_code=status.HTTP_201_CREATED)
async def create_comment(db: DBSession, post_id: int, comment_data: CommentCreate, request: Request):
    return await create_new_comment(db, post_id, comment_data, request)

@router.post("/{comment_id}/like",
             summary='Like Comment',
             status_code=status.HTTP_201_CREATED)
async def like_comment(db: DBSession, post_id: int, comment_id: int, request: Request):
    return await like_post_comment(db, post_id, comment_id, request)

@router.delete("/{comment_id}/unlike",
               summary='Unlike Comment',
               status_code=status.HTTP_204_NO_CONTENT)
async def unlike_comment(db: DBSession, post_id: int, comment_id: int, request: Request):
    return await unlike_post_comment(db, post_id, comment_id, request)