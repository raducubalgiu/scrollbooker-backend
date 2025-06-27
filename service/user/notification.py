from fastapi import Request, HTTPException
from sqlalchemy.orm import joinedload
from starlette import status

from core.crud_helpers import db_get_all
from core.dependencies import DBSession, Pagination
from models import Notification
from schema.user.notification import NotificationResponse

async def get_notifications_by_user_id(db: DBSession, pagination: Pagination, request: Request):
    auth_user_id = request.state.user.get("id")
    return await db_get_all(db,
                             model=Notification,
                             schema=NotificationResponse,
                             filters={
                                 Notification.is_deleted: False,
                                 Notification.receiver_id: auth_user_id
                             },
                             joins=[joinedload(Notification.sender)],
                             page=pagination.page,
                             limit=pagination.limit,
                             order_by="created_at",
                             descending=True)

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