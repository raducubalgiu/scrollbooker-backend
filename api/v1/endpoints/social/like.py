from fastapi import APIRouter, status, Request, Response

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination, AuthenticatedUser
from schema.social.post import UserPostResponse
from service.social.like import like_post_by_id, unlike_post_by_id, get_posts_liked_by_user_id

router = APIRouter(tags=["Likes"])

@router.get("/users/{user_id}/liked-posts",
            summary='List All Posts Likes By User Id',
            response_model=PaginatedResponse[UserPostResponse])
async def get_posts_liked_by_user(
        db: DBSession,
        user_id: int,
        pagination: Pagination,
        auth_user: AuthenticatedUser
) -> PaginatedResponse[UserPostResponse]:
    return await get_posts_liked_by_user_id(db, user_id, pagination, auth_user)

@router.post("/posts/{post_id}/likes",
             summary='Like Post By Post Id',
             status_code=status.HTTP_201_CREATED)
async def like_post(
        db: DBSession,
        post_id: int,
        auth_user: AuthenticatedUser
) -> Response:
    return await like_post_by_id(db, post_id, auth_user)

@router.delete("/posts/{post_id}/likes",
            summary='Unlike Post by Post Id',
            status_code=status.HTTP_204_NO_CONTENT)
async def unlike_post(
        db: DBSession,
        post_id: int,
        auth_user: AuthenticatedUser
) -> Response:
    return await unlike_post_by_id(db, post_id, auth_user)