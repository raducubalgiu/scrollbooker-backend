from fastapi import APIRouter
from starlette import status
from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession, SuperAdminSession
from backend.schema.booking.nomenclature.filter import FilterResponse, FilterCreate, FilterUpdate, \
    FilterWithSubFiltersResponse
from backend.service.booking.nomenclature.filter import create_new_filter, get_all_filters, \
    update_filter_by_id, delete_filter_by_id, get_sub_filters_by_filter_id, \
    get_filters_by_business_type_id
from backend.schema.booking.nomenclature.sub_filter import SubFilterResponse

router = APIRouter(tags=["Filters"])

@router.get(
    '/filters',
    summary='List All Filters',
    response_model=PaginatedResponse[FilterWithSubFiltersResponse])
async def get_filters(db: DBSession, page: int, limit: int):
    return await get_all_filters(db, page, limit)

@router.get(
    "/business-types/{business_type_id}/filters",
    summary='List All Filters - Filtered By Business Type Id',
    response_model=list[FilterWithSubFiltersResponse])
async def get_filters_by_business_type(db: DBSession, business_type_id: int):
    return await get_filters_by_business_type_id(db, business_type_id)

@router.get("/filters/{filter_id}/sub-filters", response_model=PaginatedResponse[SubFilterResponse])
async def get_sub_filters_by_filter(db: DBSession, filter_id: int, page: int, limit: int):
    return await get_sub_filters_by_filter_id(db, filter_id, page, limit)

@router.post("/filters/", response_model=FilterResponse, dependencies=[SuperAdminSession])
async def create_filter(db: DBSession, filter_create: FilterCreate):
    return await create_new_filter(db, filter_create)

@router.put("/filters/{filter_id}", response_model=FilterResponse, dependencies=[SuperAdminSession])
async def update_filter(db: DBSession, filter_update: FilterUpdate, filter_id: int):
    return await update_filter_by_id(db, filter_update, filter_id)

@router.delete("/filters/{filter_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[SuperAdminSession])
async def delete_filter(db: DBSession, filter_id: int):
    return await delete_filter_by_id(db, filter_id)