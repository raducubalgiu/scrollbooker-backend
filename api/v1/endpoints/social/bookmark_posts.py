from fastapi import APIRouter, Request, status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from schema.social.post import UserPostResponse
from service.social.bookmark_posts import bookmark_post_by_id, unbookmark_post_by_id, \
    get_bookmarked_posts_by_user

router = APIRouter(tags=["Bookmark Posts"])

@router.get("/users/{user_id}/bookmark-posts",
            summary='List All Bookmarked Posts By User',
            response_model=PaginatedResponse[UserPostResponse])
async def get_bookmarked_posts(db: DBSession, user_id: int, pagination: Pagination, request: Request):
    return await get_bookmarked_posts_by_user(db, user_id, pagination, request)

@router.post("/posts/{post_id}/bookmark-posts",
             summary='Bookmark Post By Post Id',
             status_code=status.HTTP_201_CREATED)
async def bookmark_post(db: DBSession, post_id: int, request: Request):
    return await bookmark_post_by_id(db, post_id, request)

@router.delete("/posts/{post_id}/bookmark-posts",
            summary='Unbookmark Post by Post Id',
            status_code=status.HTTP_204_NO_CONTENT)
async def unbookmark_post(db: DBSession, post_id: int, request: Request):
    return await unbookmark_post_by_id(db, post_id, request)