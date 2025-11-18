from fastapi import APIRouter, Request, Response, status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination, AuthenticatedUser
from schema.social.comment import CommentCreate, CommentResponse
from service.social.comment import get_comments_by_post_id, create_new_comment, like_post_comment, \
    unlike_post_comment, get_comments_by_parent_id

router = APIRouter(tags=["Comments"])

@router.get("/posts/{post_id}/comments",
            summary='List All Comments By Post Id',
            response_model=PaginatedResponse[CommentResponse])
async def get_comments(
        db: DBSession,
        post_id: int,
        pagination: Pagination,
        auth_user: AuthenticatedUser
) -> PaginatedResponse[CommentResponse]:
    return await get_comments_by_post_id(db, post_id, pagination, auth_user)

@router.get("/posts/{post_id}/comments/{parent_id}/replies",
            summary='List All Comment Replies',
            response_model=PaginatedResponse[CommentResponse])
async def get_comment_replies(
        db: DBSession,
        post_id: int,
        parent_id: int,
        pagination: Pagination,
        auth_user: AuthenticatedUser
) -> PaginatedResponse[CommentResponse]:
    return await get_comments_by_parent_id(db, post_id, parent_id, pagination, auth_user)

@router.post("/posts/{post_id}/comments",
             summary='Create New Comment',
             response_model=CommentResponse)
async def create_comment(
        db: DBSession,
        post_id: int,
        comment_data: CommentCreate,
        auth_user: AuthenticatedUser
) -> CommentResponse:
    return await create_new_comment(db, post_id, comment_data, auth_user)

@router.post("/comments/{comment_id}/likes",
             summary='Like Comment',
             status_code=status.HTTP_201_CREATED)
async def like_comment(
        db: DBSession,
        comment_id: int,
        auth_user: AuthenticatedUser
) -> Response:
    return await like_post_comment(db, comment_id, auth_user)

@router.delete("/comments/{comment_id}/likes",
               summary='Unlike Comment',
               status_code=status.HTTP_204_NO_CONTENT)
async def unlike_comment(
        db: DBSession,
        comment_id: int,
        auth_user: AuthenticatedUser
) -> Response:
    return await unlike_post_comment(db, comment_id, auth_user)