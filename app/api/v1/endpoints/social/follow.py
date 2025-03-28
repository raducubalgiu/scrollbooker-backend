from typing import Optional

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from app.core.dependencies import DBSession
from app.schema.social.follow import FollowResponse
from app.service.social.follow import follow_user, is_user_follow, unfollow_user

router = APIRouter(prefix="/follows", tags=["Follows"])

@router.get("/followers/{follower_id}/followings/{followee_id}", response_model=Optional[FollowResponse])
async def is_follow(db: DBSession, follower_id: int, followee_id: int):
    return await is_user_follow(db, follower_id, followee_id)

@router.post("/followers/{follower_id}/followings/{followee_id}", status_code=status.HTTP_201_CREATED)
async def follow(db: DBSession, follower_id: int, followee_id: int, request: Request):
    return await follow_user(db, follower_id, followee_id, request)

@router.delete("/followers/{follower_id}/followings/{followee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow(db: DBSession, follower_id: int, followee_id: int, request: Request):
    return await unfollow_user(db, follower_id, followee_id, request)

