from fastapi import HTTPException
from sqlalchemy import select, insert, delete
from sqlalchemy.orm import joinedload
from starlette.requests import Request
from starlette import status
from app.core.dependencies import DBSession
from app.models import Follow, User, UserCounters
from app.core.logger import logger

async def is_user_follow(db: DBSession, follower_id: int, followee_id: int):
    follower = await db.get(User, follower_id)
    followee = await db.get(User, followee_id)

    if follower and followee:
        result = await db.execute(
            select(Follow)
            .where((Follow.follower_id == follower_id) & (Follow.followee_id == followee_id)) # type: ignore
            .options(
                joinedload(Follow.follower),
                joinedload(Follow.followee)
            )
        )
        is_follow = result.scalar_one_or_none()

        return is_follow
    else:
        raise HTTPException(status_code=404, detail='User not found')

async def follow_user(db :DBSession, follower_id: int, followee_id: int, request: Request):
    is_follow = await is_user_follow(db, follower_id, followee_id)
    auth_user_id = request.state.user.get("id")

    if auth_user_id != follower_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You do not have permission to perform this action')

    if is_follow:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Already followed!')

    try:
        await db.execute(insert(Follow).values(follower_id=follower_id, followee_id=followee_id))
        query_counters = await db.execute(select(UserCounters).where(UserCounters.user_id == follower_id)) #type: ignore
        user_counters = query_counters.scalar()
        user_counters.followings_count = user_counters.followings_count + 1

        await db.commit()
        return { "detail": "Follow request was successfull" }
    except Exception as e:
        await db.rollback()
        logger.error(f"User: {followee_id} could not be followed by User: {follower_id}. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')

async def unfollow_user(db :DBSession, follower_id: int, followee_id: int, request: Request):
    is_follow = await is_user_follow(db, follower_id, followee_id)
    auth_user_id = request.state.user.get("id")

    if auth_user_id != follower_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You do not have permission to perform this action')

    if not is_follow:
        raise HTTPException(status_code=400, detail='Not follow this user!')

    try:
        await db.delete(is_follow)
        query_counters = await db.execute(
            select(UserCounters).where(UserCounters.user_id == follower_id))  # type: ignore
        user_counters = query_counters.scalar()
        user_counters.followings_count = user_counters.followings_count - 1 if user_counters.followings_count > 0 else 0

        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"User: {followee_id} could not be unfollowed by the User: {follower_id}. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')
