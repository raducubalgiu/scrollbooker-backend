from fastapi import Request, HTTPException
from sqlalchemy import select, desc, and_, literal, func
from sqlalchemy.orm import joinedload
from starlette import status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession
from models import Notification, Follow, User
from schema.user.notification import NotificationResponse

async def get_notifications_by_user_id(db: DBSession, page: int, limit: int, request: Request):
    auth_user_id = request.state.user.get("id")

    count_stmt = select(func.count()).select_from(Notification).where(
        and_(
            Notification.is_deleted == False,
            Notification.receiver_id == auth_user_id
        )
    )
    count_total = await db.execute(count_stmt)
    count = count_total.scalar_one()

    is_follow = (
        select(literal(True))
        .select_from(Follow)
        .where(and_(
            Follow.follower_id == auth_user_id,
            Follow.followee_id == User.id)
        )
        .correlate(User)
        .exists()
    )

    notifications_result = await db.execute(
        select(Notification, is_follow)
        .join(User, User.id == Notification.sender_id)
        .where(
            and_(
                Notification.is_deleted == False,
                Notification.receiver_id == auth_user_id
            )
        )
        .options(joinedload(Notification.sender))
        .order_by(desc(Notification.created_at))
        .offset((page - 1) * limit)
        .limit(limit)
    )

    notifications = []

    for notification, is_follow in notifications_result:
        notifications.append(
            NotificationResponse(
                id=notification.id,
                type=notification.type,
                sender_id=notification.sender_id,
                receiver_id=notification.receiver_id,
                data=notification.data,
                message=notification.message,
                is_read=notification.is_read,
                is_deleted=notification.is_deleted,
                sender=notification.sender,
                is_follow = is_follow
            )
        )

    return PaginatedResponse(
        count=count,
        results=notifications
    )

async def delete_notification_by_id(db: DBSession, notification_id, request: Request):
    auth_user_id = request.state.user.get("id")
    notification = await db.get(Notification, notification_id)

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Notification not found')

    if auth_user_id != notification.receiver_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='You do not have permission to perform this action')

    notification.is_deleted = True
    db.add(notification)
    await db.commit()