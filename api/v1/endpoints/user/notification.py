from fastapi import APIRouter, Response, status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, Pagination, AuthenticatedUser
from schema.user.notification import NotificationResponse
from service.user.notification import delete_notification_by_id, get_notifications_by_user_id

router = APIRouter(prefix= "/notifications",tags=["Notifications"])

@router.get("/",
    summary="List All Notifications Filtered by User Id",
    response_model=PaginatedResponse[NotificationResponse])
async def get_notifications_by_user(
        db: DBSession,
        pagination: Pagination,
        auth_user: AuthenticatedUser
) -> PaginatedResponse[NotificationResponse]:
    return await get_notifications_by_user_id(db, pagination, auth_user)

@router.delete("/{notification_id}",
    summary="Delete Notification",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
        db: DBSession,
        notification_id: int,
        auth_user: AuthenticatedUser
) -> Response:
    return await delete_notification_by_id(db, notification_id, auth_user)