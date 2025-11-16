from typing import Optional

from fastapi import HTTPException, Request, Response, status
from sqlalchemy import select, insert, and_, update, func, delete

from core.dependencies import DBSession
from core.enums.follow_type import FollowTypeEnum
from core.enums.notification_type import NotificationTypeEnum
from models import Follow, User, UserCounters, Notification
from schema.social.follow import FollowResponse

async def _update_counters(
        db: DBSession,
        followee_id: int,
        follower_id: int,
        action_type: FollowTypeEnum
) -> None:
    delta = 1 if action_type == FollowTypeEnum.FOLLOW else -1

    # Target User (followers count)
    await db.execute(
        update(UserCounters)
        .where(UserCounters.user_id == followee_id)
        .values(followers_count=func.greatest(UserCounters.followers_count + delta, 0))
    )

    # Authenticated User: followings_count
    await db.execute(
        update(UserCounters)
        .where(UserCounters.user_id == follower_id)
        .values(followings_count=func.greatest(UserCounters.followings_count + delta, 0))
    )

async def is_user_follow(
        db: DBSession,
        followee_id: int,
        request: Request
) -> Optional[FollowResponse]:
    follower_id = request.state.user.get("id")

    follower = await db.get(User, follower_id)
    followee = await db.get(User, followee_id)

    if follower and followee:
        result = await db.execute(
            select(Follow)
            .where(and_(
                Follow.follower_id == follower_id,
                Follow.followee_id == followee_id
            ))
        )

        is_follow = result.scalar_one_or_none()
        return is_follow
    else:
        raise HTTPException(status_code=404, detail='User not found')

async def follow_user(
        db :DBSession,
        followee_id: int,
        request: Request
) -> Response:
    async with db.begin():
        follower_id = request.state.user.get("id")

        # Check Follow
        if await is_user_follow(db, followee_id, request):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Already followed!')

        # Follow
        await db.execute(
            insert(Follow)
            .values(follower_id=follower_id, followee_id=followee_id))

        # Update Counters
        await _update_counters(
            db=db,
            followee_id=followee_id,
            follower_id=follower_id,
            action_type=FollowTypeEnum.FOLLOW
        )

        # Send Followee follow notification
        notification = Notification(
            type=NotificationTypeEnum.FOLLOW,
            sender_id=follower_id,
            receiver_id=followee_id,
            data={},
            message=None
        )
        db.add(notification)

        return Response(status_code=status.HTTP_201_CREATED)

async def unfollow_user(
        db :DBSession,
        followee_id: int,
        request: Request
) -> Response:
    async with db.begin():
        follower_id = request.state.user.get("id")

        # Check Follow
        if not await is_user_follow(db, followee_id, request):
            raise HTTPException(status_code=400, detail='Not follow this user!')

        # Unfollow
        await db.execute(
            delete(Follow).where(and_(
                Follow.follower_id == follower_id,
                Follow.followee_id == followee_id
            ))
        )

        # Update Counters
        await _update_counters(
            db=db,
            followee_id=followee_id,
            follower_id=follower_id,
            action_type=FollowTypeEnum.UNFOLLOW
        )

        return Response(status_code=status.HTTP_204_NO_CONTENT)
