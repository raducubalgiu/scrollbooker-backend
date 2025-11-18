from typing import Optional, List

from fastapi import APIRouter, Query, status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination, AuthenticatedUser
from schema.social.post import PostCreate, UserPostResponse
from service.social.post import create_new_post, get_posts_by_user_id, get_following_posts, \
    get_explore_feed_posts, get_video_reviews_by_user_id

router = APIRouter(tags=["Posts"])

@router.get("/posts/explore",
            summary='Get User Book Now Feed',
            response_model=PaginatedResponse[UserPostResponse])
async def get_explore_feed(
        db: DBSession,
        pagination: Pagination,
        auth_user: AuthenticatedUser,
        business_types: Optional[List[int]] = Query(default=None)
) -> PaginatedResponse[UserPostResponse]:
    return await get_explore_feed_posts(db, pagination, auth_user, business_types)

@router.get("/posts/following",
            summary='Get User Following Posts',
            response_model=PaginatedResponse[UserPostResponse])
async def get_following(
        db: DBSession,
        pagination: Pagination,
        auth_user: AuthenticatedUser
) -> PaginatedResponse[UserPostResponse]:
    return await get_following_posts(db, pagination, auth_user)

@router.get("/users/{user_id}/posts",
            summary='List All Posts By User Id',
            response_model=PaginatedResponse[UserPostResponse])
async def get_posts_by_user(
        db: DBSession,
        user_id: int,
        pagination: Pagination,
        auth_user: AuthenticatedUser
) -> PaginatedResponse[UserPostResponse]:
    return await get_posts_by_user_id(db, user_id, pagination, auth_user)

@router.get("/users/{user_id}/posts/video-reviews",
            summary='List All Posts Video Reviews By User Id',
            response_model=PaginatedResponse[UserPostResponse])
async def get_video_reviews_by_user(
        db: DBSession,
        user_id: int,
        pagination: Pagination,
        auth_user: AuthenticatedUser
) -> PaginatedResponse[UserPostResponse]:
    return await get_video_reviews_by_user_id(db, user_id, pagination, auth_user)

@router.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(
        db: DBSession,
        post_create: PostCreate,
        auth_user: AuthenticatedUser
):
    return await create_new_post(db, post_create, auth_user)
