from typing import Optional, List

from fastapi import APIRouter, Query
from starlette import status
from starlette.requests import Request

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from schema.social.post import PostCreate, UserPostResponse
from schema.social.comment import CommentCreate, CommentBase
from service.social.post import create_new_post, get_posts_by_user_id, get_book_now_posts, get_following_posts
from service.social.comment import create_new_comment, like_post_comment, unlike_post_comment, get_comments_by_post_id

router = APIRouter(tags=["Posts"])

@router.get("/posts/book-now",
            summary='Get User Book Now Feed')
async def get_book_now(
        db: DBSession,
        pagination: Pagination,
        request: Request,
        business_types: Optional[List[int]] = Query(default=None)
):
    return await get_book_now_posts(db, pagination, request, business_types)

@router.get("/posts/following")
async def get_following(db: DBSession, pagination: Pagination, request: Request):
    return await get_following_posts(db, pagination, request)

@router.get("/users/{user_id}/posts",
            summary='List All Posts By User Id',
            response_model=PaginatedResponse[UserPostResponse])
async def get_posts_by_user(db: DBSession, user_id: int, pagination: Pagination, request: Request):
    return await get_posts_by_user_id(db, user_id, pagination, request)

@router.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(db: DBSession, post_create: PostCreate, request: Request):
    return await create_new_post(db, post_create, request)
