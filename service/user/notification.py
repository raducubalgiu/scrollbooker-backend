from fastapi import Request, HTTPException
from sqlalchemy.orm import joinedload
from starlette import status

from backend.core.crud_helpers import db_get_all
from backend.core.dependencies import DBSession
from backend.models import Notification
from backend.schema.user.notification import NotificationResponse

async def get_notifications_by_user_id(db: DBSession, page: int, limit: int):
    return await db_get_all(db,
                             model=Notification,
                             schema=NotificationResponse,
                             filters={Notification.is_deleted: False},
                             joins=[joinedload(Notification.sender)],
                             page=page,
                             limit=limit)

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