from starlette.requests import Request
from fastapi import APIRouter
from starlette import status
from backend.core.dependencies import DBSession
from backend.schema.social.repost import RepostCreate
from backend.service.social.repost import repost_post_by_id, unrepost_post_by_id

router = APIRouter(tags=["Reposts"])

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