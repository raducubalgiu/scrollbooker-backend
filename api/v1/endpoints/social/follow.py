from typing import Optional
from fastapi import APIRouter, Request, status

from core.dependencies import DBSession
from schema.social.follow import FollowResponse
from service.social.follow import follow_user, is_user_follow, unfollow_user

router = APIRouter(prefix="/follows/{followee_id}",  tags=["Follows"])

@router.get("/",
    summary='Check Follow',
    response_model=Optional[FollowResponse])
async def is_follow(db: DBSession, followee_id: int, request: Request):
    return await is_user_follow(db, followee_id, request)

@router.post("/",
     summary='Follow User',
     status_code=status.HTTP_201_CREATED)
async def follow(db: DBSession, followee_id: int, request: Request):
    return await follow_user(db, followee_id, request)

@router.delete(
    "/",
    summary='Unfollow User',
    status_code=status.HTTP_204_NO_CONTENT)
async def unfollow(db: DBSession, followee_id: int, request: Request):
    return await unfollow_user(db, followee_id, request)

