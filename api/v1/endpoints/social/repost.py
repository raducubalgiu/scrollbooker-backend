from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination
from schema.social.post import UserPostResponse
from schema.social.repost import RepostCreate
from service.social.repost import repost_post_by_id, unrepost_post_by_id, get_reposts_by_user

router = APIRouter(tags=["Reposts"])

@router.get("/users/{user_id}/reposts",
            summary='List All Reposts By User Id',
            response_model=PaginatedResponse[UserPostResponse])
async def get_reposts(db: DBSession, user_id: int, pagination: Pagination):
    return await get_reposts_by_user(db, user_id, pagination)

@router.post("/posts/{post_id}/reposts",
             summary='Repost Post By Post Id',
             status_code=status.HTTP_201_CREATED)
async def repost_post(db: DBSession, post_id: int, repost_create: RepostCreate, request: Request):
    return await repost_post_by_id(db, post_id, repost_create, request)

@router.delete("/posts/{post_id}/reposts",
               summary='Unrepost post By Post Id',
               status_code=status.HTTP_204_NO_CONTENT)
async def unrepost_post(db: DBSession, post_id: int, request: Request):
    return await unrepost_post_by_id(db, post_id, request)