from fastapi import APIRouter, Query, Request, status
from typing import List, Optional

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, HTTPClient, RedisClient, SuperAdminSession, Pagination
from core.dependencies import BusinessSession
from schema.booking.business import BusinessCreate, BusinessResponse, BusinessHasEmployeesUpdate, \
    BusinessCreateResponse, BusinessLocationResponse, BusinessEmployeeResponse
from service.booking.business import get_businesses_by_distance, create_new_business, get_business_employees_by_id, \
    get_business_by_user_id, update_business_has_employees, \
    get_business_by_id, get_user_recommended_businesses, get_business_location, get_all_unapproved_businesses, \
    approve_business_by_owner_id

router = APIRouter(tags=["Businesses"])

@router.post(
    "/businesses",
    summary='Create New Business',
    response_model=BusinessCreateResponse,
    dependencies=[BusinessSession])
async def create_business(db: DBSession, client: HTTPClient, business_data: BusinessCreate, request: Request):
    return await create_new_business(db, client, business_data, request)

@router.get("/businesses/{business_id}/location",
            response_model=BusinessLocationResponse)
async def business_location(
        db: DBSession,
        http_client: HTTPClient,
        redis_client: RedisClient,
        business_id: int,
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None,
):
    return await get_business_location(db, http_client, redis_client, business_id, user_lat, user_lng)

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
    "/users/{user_id}/businesses",
    summary='Get Business By User Id',
    response_model=BusinessResponse)
async def get_business_by_user(db: DBSession, user_id: int):
    return await get_business_by_user_id(db, user_id)

@router.get(
    "/businesses/{business_id}/employees",
    summary='List Employees filtered By Business Id',
    response_model=PaginatedResponse[BusinessEmployeeResponse],
    dependencies=[BusinessSession])
async def get_business_employees(db: DBSession, business_id: int, pagination: Pagination):
    return await get_business_employees_by_id(db, business_id, pagination)

@router.patch("/businesses/update-has-employees",
              summary='Update Business has employees',
              response_model=BusinessResponse,
              dependencies=[BusinessSession])
async def update_has_employees(db: DBSession, business_update: BusinessHasEmployeesUpdate, request: Request):
    return await update_business_has_employees(db, business_update, request)

@router.get("/businesses/unapproved-businesses",
            summary='List All Businesses which waits for the approval',
            dependencies=[SuperAdminSession])
async def get_unapproved_businesses(db: DBSession, pagination: Pagination):
    return await get_all_unapproved_businesses(db, pagination)

@router.post("/users/{user_id}/approve",
            summary='Approve Business and its Owner based on Owner Id',
            dependencies=[SuperAdminSession],
            status_code=status.HTTP_204_NO_CONTENT)
async def approve_business(db: DBSession, user_id: int):
    return await approve_business_by_owner_id(db, user_id)

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

@router.get(
    "/businesses/{business_id}",
    summary='Get Business By Id',
    response_model=BusinessResponse)
async def get_business_by_user(db: DBSession, business_id: int):
    return await get_business_by_id(db, business_id)