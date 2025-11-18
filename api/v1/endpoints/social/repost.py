from fastapi import APIRouter, Request, Response, status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination, AuthenticatedUser
from schema.social.post import UserPostResponse
from schema.social.repost import RepostCreate
from service.social.repost import repost_post_by_id, un_repost_post_by_id, get_reposts_by_user

router = APIRouter(tags=["Reposts"])

@router.get("/users/{user_id}/reposts",
            summary='List All Reposts By User Id',
            response_model=PaginatedResponse[UserPostResponse])
async def get_reposts(
        db: DBSession,
        user_id: int,
        pagination: Pagination,
        auth_user: AuthenticatedUser
) -> PaginatedResponse[UserPostResponse]:
    return await get_reposts_by_user(db, user_id, pagination, auth_user)

@router.post("/posts/{post_id}/reposts",
             summary='Repost Post By Post Id',
             status_code=status.HTTP_201_CREATED)
async def repost_post(
        db: DBSession,
        post_id: int,
        repost_create: RepostCreate,
        auth_user: AuthenticatedUser
) -> Response:
    return await repost_post_by_id(db, post_id, repost_create, auth_user)

@router.delete("/posts/{post_id}/reposts",
               summary='UnRepost Post By Post Id',
               status_code=status.HTTP_204_NO_CONTENT)
async def un_repost_post(
        db: DBSession,
        post_id: int,
        auth_user: AuthenticatedUser
) -> Response:
    return await un_repost_post_by_id(db, post_id, auth_user)