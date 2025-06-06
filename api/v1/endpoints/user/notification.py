from fastapi import APIRouter, Request
from starlette import status

from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession, Pagination
from backend.schema.user.notification import NotificationResponse
from backend.service.user.notification import delete_notification_by_id, get_notifications_by_user_id

router = APIRouter(prefix= "/notifications",tags=["Notifications"])

@router.get("/",
    summary="List All Notifications Filtered by User Id",
    response_model=PaginatedResponse[NotificationResponse])
async def get_notifications_by_user(db: DBSession, pagination: Pagination, request: Request):
    return await get_notifications_by_user_id(db, pagination, request)

@router.delete("/{notification_id}",
    summary="Delete Notification",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(db: DBSession, notification_id: int, request: Request):
    return await delete_notification_by_id(db, notification_id, request)