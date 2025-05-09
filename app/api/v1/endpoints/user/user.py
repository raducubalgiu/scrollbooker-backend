from fastapi import APIRouter, Query
from starlette.requests import Request
from app.core.dependencies import DBSession
from app.schema.booking.schedule import ScheduleResponse
from app.schema.user.user import UserBaseMinimum
from app.service.user.user import get_user_followers_by_user_id, \
    get_user_followings_by_user_id, get_user_dashboard_summary_by_id, \
    get_available_professions_by_user_id, search_users_clients, get_product_durations_by_user_id

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/search", response_model=list[UserBaseMinimum])
async def search_users_as_clients(db: DBSession, q: str):
    return await search_users_clients(db, q)

@router.get("/{user_id}/dashboard-summary")
async def get_user_dashboard_summary(db: DBSession, user_id: int, start_date: str, end_date: str, all_employees: bool = Query(False)):
    return await get_user_dashboard_summary_by_id(db, user_id, start_date, end_date, all_employees)

@router.get("/{user_id}/product-durations", response_model=list[int])
async def get_user_product_durations(db:DBSession, user_id: int):
    return await get_product_durations_by_user_id(db, user_id)

@router.get("/{user_id}/followers", response_model=list[UserBaseMinimum])
async def get_user_followers(db: DBSession, user_id: int, page: int, limit: int, request: Request):
    return await get_user_followers_by_user_id(db, user_id, page, limit, request)

@router.get("/{user_id}/followings", response_model=list[UserBaseMinimum])
async def get_user_followings(db: DBSession, user_id: int, page: int, limit: int, request: Request):
    return await get_user_followings_by_user_id(db, user_id, page, limit, request)

@router.get("/{user_id}/available-professions")
async def get_user_available_professions(db: DBSession, user_id: int):
    return await get_available_professions_by_user_id(db, user_id)
