from fastapi import APIRouter, Query
from starlette import status
from starlette.requests import Request
from typing import List
from core.dependencies import DBSession
from core.dependencies import BusinessSession
from schema.booking.business import BusinessCreate, BusinessResponse, BusinessPlaceAddressResponse
from schema.nomenclature.service import ServiceIdsUpdate
from service.booking.business import attach_service_to_business, get_businesses_by_distance, create_new_business, \
    delete_business_by_id, detach_service_from_business, get_business_employees_by_id, \
    attach_many_services_to_business, get_business_by_user_id
from service.integration.google_places import search_places

router = APIRouter(tags=["Businesses"])

@router.post(
    "/businesses",
    summary='Create New Business',
    status_code=status.HTTP_201_CREATED,
    dependencies=[BusinessSession])
async def create_business(db: DBSession, business_data: BusinessCreate):
    return await create_new_business(db, business_data)

@router.get("/businesses/search",
            summary='Search Business address',
            response_model=list[BusinessPlaceAddressResponse])
async def search_business_address(query: str = Query(min_length=2)):
    return await search_places(query)

@router.get(
    "/users/{user_id}/business",
    summary='Get Business By User Id',
    response_model=BusinessResponse)
async def get_business_by_user(db: DBSession, user_id: int):
    return await get_business_by_user_id(db, user_id)

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
    "/businesses/{business_id}/employees",
    summary='List Employees filtered By Business Id')
async def get_business_employees(db: DBSession, business_id: int, page: int, limit: int):
    return await get_business_employees_by_id(db, business_id, page, limit)

@router.delete(
    "/businesses/{business_id}",
    summary='Delete Business',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[BusinessSession])
async def delete_business(db: DBSession, business_id: int, request: Request):
    return await delete_business_by_id(db, business_id, request)

@router.post(
    "/businesses/{business_id}/services/{service_id}",
    summary='Attach Service To Business',
    status_code=status.HTTP_201_CREATED,
    dependencies=[BusinessSession])
async def attach_services(db: DBSession, business_id: int, service_id: int, request: Request):
    return await attach_service_to_business(db, business_id, service_id, request)

@router.post(
    "/businesses/{business_id}/services",
    summary='Attach Many Services To Business',
    status_code=status.HTTP_201_CREATED,
    dependencies=[BusinessSession])
async def attach_many_services(db: DBSession, business_id: int, service_ids: ServiceIdsUpdate, request: Request):
    return await attach_many_services_to_business(db, business_id, service_ids, request)

@router.delete(
    "/businesses/{business_id}/services/{service_id}",
    summary='Remove Service From Business',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[BusinessSession])
async def detach_services(db: DBSession, business_id: int, service_id: int, request: Request):
    return await detach_service_from_business(db, business_id, service_id, request)

