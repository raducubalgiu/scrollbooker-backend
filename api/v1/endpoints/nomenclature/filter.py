from typing import Union

from fastapi import APIRouter
from starlette import status
from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, SuperAdminSession
from schema.nomenclature.filter import FilterResponse, FilterCreate, FilterUpdate, FilterWithSubFiltersResponse
from service.nomenclature.filter import create_new_filter, get_all_filters, \
    update_filter_by_id, delete_filter_by_id, get_filters_by_business_type_id, attach_filters_to_business_type, detach_filters_from_business_type

router = APIRouter(tags=["Filters"])

@router.get('/filters',
    summary='List All Filters',
    response_model=Union[PaginatedResponse[FilterWithSubFiltersResponse], list[FilterWithSubFiltersResponse]])
async def get_filters(db: DBSession, page: int, limit: int):
    return await get_all_filters(db, page, limit)

@router.get("/business-types/{business_type_id}/filters",
    summary='List All Filters - Filtered By Business Type Id',
    response_model=list[FilterWithSubFiltersResponse])
async def get_filters_by_business_type(db: DBSession, business_type_id: int):
    return await get_filters_by_business_type_id(db, business_type_id)

@router.post("/filters",
     response_model=FilterResponse,
     summary='Create New Filter',
     dependencies=[SuperAdminSession])
async def create_filter(db: DBSession, filter_create: FilterCreate):
    return await create_new_filter(db, filter_create)

@router.put("/filters/{filter_id}",
    summary='Update Filter',
    response_model=FilterResponse,
    dependencies=[SuperAdminSession])
async def update_filter(db: DBSession, filter_update: FilterUpdate, filter_id: int):
    return await update_filter_by_id(db, filter_update, filter_id)

@router.delete("/filters/{filter_id}",
    summary='Delete Filter',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def delete_filter(db: DBSession, filter_id: int):
    return await delete_filter_by_id(db, filter_id)

@router.post("/filters/{filter_id}/business-types/{business_type_id}",
    summary='Attach Filter - Business Type',
    status_code=status.HTTP_201_CREATED,
    dependencies=[SuperAdminSession])
async def attach_filters_business_type(db: DBSession, business_type_id: int, filter_id: int):
    return await attach_filters_to_business_type(db, business_type_id, filter_id)

@router.delete("/filters/{filter_id}/business-types/{business_type_id}",
    summary='Detach Filter - Business Type',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def detach_filters_business_type(db: DBSession, business_type_id: int, filter_id: int):
    return await detach_filters_from_business_type(db, business_type_id, filter_id)