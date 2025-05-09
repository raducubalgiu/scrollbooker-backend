from fastapi import APIRouter, Request
from starlette import status

from app.core.crud_helpers import PaginatedResponse
from app.core.dependencies import DBSession
from app.schema.user.notification import NotificationResponse
from app.service.user.notification import delete_notification_by_id, get_notifications_by_user_id

router = APIRouter(tags=["Notifications"])

@router.get(
    "/users/{user_id}/notifications",
    summary="List All Notifications Filtered by User Id",
    response_model=PaginatedResponse[NotificationResponse])
async def get_notifications_by_user(db: DBSession, page: int, limit: int):
    return await get_notifications_by_user_id(db, page, limit)

@router.delete(
    "/notifications/{notification_id}",
    summary="Delete Notification",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(db: DBSession, notification_id: int, request: Request):
    return await delete_notification_by_id(db, notification_id, request)