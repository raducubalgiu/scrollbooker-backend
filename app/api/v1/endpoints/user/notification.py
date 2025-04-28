from fastapi import APIRouter, Request
from starlette import status

from app.core.dependencies import DBSession
from app.service.user.notification import delete_notification_by_id

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(db: DBSession, notification_id: int, request: Request):
    return await delete_notification_by_id(db, notification_id, request)