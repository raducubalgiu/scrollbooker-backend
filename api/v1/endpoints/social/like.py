from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from core.dependencies import DBSession
from service.social.like import like_post_by_id, unlike_post_by_id

router = APIRouter(tags=["Likes"])

@router.post("/posts/{post_id}/likes",
             summary='Like Post By Post Id',
             status_code=status.HTTP_201_CREATED)
async def like_post(db: DBSession, post_id: int, request: Request):
    return await like_post_by_id(db, post_id, request)

@router.delete("/posts/{post_id}/likes",
            summary='Unlike Post by Post Id',
            status_code=status.HTTP_204_NO_CONTENT)
async def unlike_post(db: DBSession, post_id: int, request: Request):
    return await unlike_post_by_id(db, post_id, request)