from fastapi import Request, HTTPException
from starlette import status
from app.core.dependencies import DBSession
from app.models import Notification

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