from fastapi import APIRouter
from starlette.requests import Request

from app.core.dependencies import DBSession
from app.schema.booking.schedule import ScheduleResponse
from app.schema.user.user import UserBaseMinimum
from app.service.booking.review import get_business_and_employee_reviews
from app.service.user.user import get_schedules_by_user_id, get_user_followers_by_user_id, \
    get_user_followings_by_user_id, get_user_dashboard_summary_by_id

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}/dashboard-summary")
async def get_user_dashboard_summary(db: DBSession, user_id: int, start_date: str, end_date: str):
    return await get_user_dashboard_summary_by_id(db, user_id, start_date, end_date)

# Get User Schedules
@router.get("/{user_id}/schedules")
async def get_user_schedules(db: DBSession, user_id: int):
    return await get_schedules_by_user_id(db, user_id)

@router.get("/{user_id}/reviews/owner-reviews")
async def get_author_reviews(db: DBSession, user_id: int, page: int, limit: int, request: Request):
    return await get_business_and_employee_reviews(db, user_id, page, limit, request)

@router.get("/{user_id}/followers", response_model=list[UserBaseMinimum])
async def get_user_followers(db: DBSession, user_id: int, page: int, limit: int, request: Request):
    return await get_user_followers_by_user_id(db, user_id, page, limit, request)

@router.get("/{user_id}/followings", response_model=list[UserBaseMinimum])
async def get_user_followings(db: DBSession, user_id: int, page: int, limit: int, request: Request):
    return await get_user_followings_by_user_id(db, user_id, page, limit, request)

# Get User Appointment

# Get User Products