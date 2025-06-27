from fastapi import HTTPException
from sqlalchemy import select, insert, delete
from sqlalchemy.orm import joinedload
from starlette.requests import Request
from starlette import status
from core.dependencies import DBSession
from models import Follow, User, UserCounters, Notification
from core.logger import logger

async def is_user_follow(db: DBSession, followee_id: int, request: Request):
    follower_id = request.state.user.get("id")
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

async def follow_user(db :DBSession, followee_id: int, request: Request):
    follower_id = request.state.user.get("id")
    is_follow = await is_user_follow(db, follower_id, request)

    if is_follow:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Already followed!')

    try:
        await db.execute(insert(Follow).values(follower_id=follower_id, followee_id=followee_id))
        query_follower_counters = await db.execute(select(UserCounters).where(UserCounters.user_id == follower_id)) #type: ignore
        query_followee_counters = await db.execute(select(UserCounters).where(UserCounters.user_id == followee_id)) #type: ignore
        follower_counters = query_follower_counters.scalar()
        followee_counters = query_followee_counters.scalar()

        follower_counters.followings_count = follower_counters.followings_count + 1
        followee_counters.followers_count = followee_counters.followers_count + 1

        notification = Notification(
            type="follow",
            sender_id=follower_id,
            receiver_id=followee_id,
            data={},
            message=None
        )
        db.add(notification)

        await db.commit()
        return { "detail": "Follow request was successfully" }
    except Exception as e:
        await db.rollback()
        logger.error(f"User: {followee_id} could not be followed by User: {follower_id}. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')

async def unfollow_user(db :DBSession, followee_id: int, request: Request):
    is_follow = await is_user_follow(db, followee_id, request)
    follower_id = request.state.user.get("id")

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
