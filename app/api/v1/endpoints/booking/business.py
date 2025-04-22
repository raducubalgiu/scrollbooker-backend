from fastapi import APIRouter, Query
from starlette import status
from starlette.requests import Request
from typing import List
from app.core.dependencies import DBSession
from app.core.dependencies import BusinessSession
from app.schema.booking.business import BusinessCreate
from app.schema.booking.nomenclature.service import ServiceIdsUpdate
from app.service.booking.business import attach_service_to_business, get_businesses_by_distance, create_new_business, \
    delete_business_by_id, detach_service_from_business, get_business_employees_by_id, get_business_by_id, \
    attach_many_services_to_business

router = APIRouter(prefix="/businesses", tags=["Businesses"])

@router.get("/{business_id}")
async def get_business(db: DBSession, business_id: int):
    return await get_business_by_id(db, business_id)

@router.get("/nearby")
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

@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[BusinessSession])
async def create_business(db: DBSession, business_data: BusinessCreate):
    return await create_new_business(db, business_data)

@router.get("/{business_id}/employees")
async def get_business_employees(db: DBSession, business_id: int, page: int, limit: int):
    return await get_business_employees_by_id(db, business_id, page, limit)

@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[BusinessSession])
async def delete_business(db: DBSession, business_id: int, request: Request):
    return await delete_business_by_id(db, business_id, request)

@router.post("/{business_id}/services/{service_id}", status_code=status.HTTP_201_CREATED, dependencies=[BusinessSession])
async def attach_services(db: DBSession, business_id: int, service_id: int, request: Request):
    return await attach_service_to_business(db, business_id, service_id, request)

@router.post("/{business_id}/services", status_code=status.HTTP_201_CREATED, dependencies=[BusinessSession])
async def attach_many_services(db: DBSession, business_id: int, service_ids: ServiceIdsUpdate, request: Request):
    return await attach_many_services_to_business(db, business_id, service_ids, request)

@router.delete("/{business_id}/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[BusinessSession])
async def detach_services(db: DBSession, business_id: int, service_id: int, request: Request):
    return await detach_service_from_business(db, business_id, service_id, request)

