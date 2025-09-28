from fastapi import APIRouter, Query
from starlette import status
from starlette.requests import Request
from typing import List, Optional
from core.dependencies import DBSession
from core.dependencies import BusinessSession
from schema.booking.business import BusinessCreate, BusinessResponse, BusinessPlaceAddressResponse, \
    BusinessHasEmployeesUpdate, BusinessCreateResponse
from service.booking.business import get_businesses_by_distance, create_new_business, \
    delete_business_by_id, get_business_employees_by_id, get_business_by_user_id, update_business_has_employees, \
    get_business_by_id, get_user_recommended_businesses
from service.integration.google_places import search_places

router = APIRouter(tags=["Businesses"])

@router.post(
    "/businesses",
    summary='Create New Business',
    response_model=BusinessCreateResponse,
    dependencies=[BusinessSession])
async def create_business(db: DBSession, business_data: BusinessCreate, request: Request):
    return await create_new_business(db, business_data, request)

@router.get("/businesses/search",
            summary='Search Business address',
            response_model=list[BusinessPlaceAddressResponse])
async def search_business_address(query: str = Query(min_length=2)):
    return await search_places(query)

@router.get("/businesses/recommended",
            summary='List Recommended Businesses')
async def get_recommended_businesses(
        db: DBSession,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        timezone: Optional[str] = None,
        limit: Optional[int] = 10):
    return await get_user_recommended_businesses(db, lat, lng, timezone, limit)

@router.get(
    "/businesses/{business_id}",
    summary='Get Business By Id',
    response_model=BusinessResponse)
async def get_business_by_user(db: DBSession, business_id: int):
    return await get_business_by_id(db, business_id)

@router.get(
    "/users/{user_id}/businesses",
    summary='Get Business By User Id',
    response_model=BusinessResponse)
async def get_business_by_user(db: DBSession, user_id: int):
    return await get_business_by_user_id(db, user_id)

@router.get(
    "/businesses/{business_id}/employees",
    summary='List Employees filtered By Business Id')
async def get_business_employees(db: DBSession, business_id: int, page: int, limit: int):
    return await get_business_employees_by_id(db, business_id, page, limit)

@router.patch("/businesses/update-has-employees",
              summary='Update Business has employees',
              response_model=BusinessResponse,
              dependencies=[BusinessSession])
async def update_has_employees(db: DBSession, business_update: BusinessHasEmployeesUpdate, request: Request):
    return await update_business_has_employees(db, business_update, request)

@router.delete(
    "/businesses/{business_id}",
    summary='Delete Business',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[BusinessSession])
async def delete_business(db: DBSession, business_id: int, request: Request):
    return await delete_business_by_id(db, business_id, request)

@router.get("/businesses/nearby")
async def get_nearby_businesses(db: DBSession,
                                lon: float,
                                lat: float,
                                start_date: str,
                                end_date: str,
                                start_time: str,
                                end_time: str,
                                service_id: int,
                                instant_booking: bool,
                                request: Request,
                                page: int,
                                limit: int,
                                sub_filters: List[int] = Query([])):
    return await get_businesses_by_distance(db, lon, lat, start_date, end_date, start_time, end_time, service_id, instant_booking, request, page, limit, sub_filters)

