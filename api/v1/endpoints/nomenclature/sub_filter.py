from typing import Union

from fastapi import APIRouter
from starlette import status

from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession, SuperAdminSession, Pagination
from backend.schema.nomenclature.sub_filter import SubFilterCreate, SubFilterResponse, SubFilterUpdate
from backend.service.nomenclature.sub_filter import create_new_sub_filter, update_sub_filter_by_id, \
    delete_sub_filters_by_id, get_sub_filters_by_filter_id

router = APIRouter(tags=["SubFilters"])

@router.get("/filters/{filter_id}/sub-filters",
    summary='List All SubFilters Filtered By Filter Id',
    response_model=Union[PaginatedResponse[SubFilterResponse], list[SubFilterResponse]])
async def get_sub_filters_by_filter(db: DBSession, filter_id: int, pagination: Pagination):
    return await get_sub_filters_by_filter_id(db, filter_id, pagination)

@router.post("/sub-filters",
     summary='Create New Filter',
     response_model=SubFilterResponse,
     dependencies=[SuperAdminSession])
async def create_sub_filter(db: DBSession, sub_filter_create: SubFilterCreate):
    return await create_new_sub_filter(db, sub_filter_create)

@router.put("/sub-filters/{sub_filter_id}",
    summary='Update SubFilter',
    response_model=SubFilterResponse,
    dependencies=[SuperAdminSession])
async def update_sub_filter(db: DBSession, sub_filter_update: SubFilterUpdate, sub_filter_id: int):
    return await update_sub_filter_by_id(db, sub_filter_update, sub_filter_id)

@router.delete("/sub-filters/{sub_filter_id}",
    summary='Delete SubFilter',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def delete_sub_filter(db: DBSession, sub_filter_id: int):
    return await delete_sub_filters_by_id(db, sub_filter_id)
