from fastapi import APIRouter, Query
from starlette import status
from starlette.requests import Request

from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession
from backend.schema.user.user import UserBaseMinimum, UsernameUpdate, FullNameUpdate, BioUpdate, GenderUpdate
from backend.service.user.user import get_user_followers_by_user_id, \
    get_user_followings_by_user_id, get_user_dashboard_summary_by_id, \
    get_available_professions_by_user_id, search_users_clients, get_product_durations_by_user_id, update_user_fullname, \
    update_user_username, update_user_bio, get_user_profile_by_id, update_user_gender

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}/user-profile")
async def get_user_profile(db: DBSession, user_id: int, request: Request):
    return await get_user_profile_by_id(db, user_id, request)

@router.patch("/user-info/fullname", status_code=status.HTTP_200_OK)
async def update_fullname(db: DBSession, fullname_update: FullNameUpdate, request: Request):
    return await update_user_fullname(db, fullname_update, request)

@router.patch("/user-info/gender", status_code=status.HTTP_200_OK)
async def update_gender(db: DBSession, gender_update: GenderUpdate, request: Request):
    return await update_user_gender(db, gender_update, request)

@router.patch("/user-info/username")
async def update_username(db: DBSession, username_update: UsernameUpdate, request: Request):
    return await update_user_username(db, username_update, request)

@router.patch("/user-info/bio")
async def update_bio(db: DBSession, bio_update: BioUpdate, request: Request):
    return await update_user_bio(db, bio_update, request)

@router.get("/search", response_model=list[UserBaseMinimum])
async def search_users_as_clients(db: DBSession, q: str):
    return await search_users_clients(db, q)

@router.get("/{user_id}/dashboard-summary")
async def get_user_dashboard_summary(db: DBSession, user_id: int, start_date: str, end_date: str, all_employees: bool = Query(False)):
    return await get_user_dashboard_summary_by_id(db, user_id, start_date, end_date, all_employees)

@router.get("/{user_id}/product-durations", response_model=list[int])
async def get_user_product_durations(db:DBSession, user_id: int):
    return await get_product_durations_by_user_id(db, user_id)

@router.get("/{user_id}/followers", response_model=PaginatedResponse[UserBaseMinimum])
async def get_user_followers(db: DBSession, user_id: int, page: int, limit: int, request: Request):
    return await get_user_followers_by_user_id(db, user_id, page, limit, request)

@router.get("/{user_id}/followings", response_model=PaginatedResponse[UserBaseMinimum])
async def get_user_followings(db: DBSession, user_id: int, page: int, limit: int, request: Request):
    return await get_user_followings_by_user_id(db, user_id, page, limit, request)

@router.get("/{user_id}/available-professions")
async def get_user_available_professions(db: DBSession, user_id: int):
    return await get_available_professions_by_user_id(db, user_id)
