from typing import Union
from fastapi import APIRouter
from starlette import status

from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession, SuperAdminSession, Pagination
from backend.schema.booking.nomenclature.business_type import BusinessTypeResponse, BusinessTypeCreate, BusinessTypeUpdate
from backend.service.booking.nomenclature.business_type import create_new_business_type, \
    delete_business_type_by_id, update_business_type_by_id, \
    attach_filters_to_business_type, attach_professions_to_business_type, detach_professions_from_business_type, \
    detach_filters_from_business_type, get_business_types_by_business_domain_id, get_business_types_by_service_id

router = APIRouter(tags=["Business Types"])

@router.get(
    "/business-domains/{business_domain_id}/business-types",
    summary='List All Business Types Filtered By Business Domain Id',
    response_model=Union[PaginatedResponse[BusinessTypeResponse], list[BusinessTypeResponse]])
async def get_business_types_by_business_domain(db: DBSession, business_domain_id: int, pagination: Pagination):
    return await get_business_types_by_business_domain_id(db, business_domain_id, pagination)

@router.get(
    "/services/{service_id}/business-types",
    summary='List All Business Types Filtered By Service Id',
    response_model=list[BusinessTypeResponse])
async def get_business_types_by_service(db: DBSession, service_id: int):
    return await get_business_types_by_service_id(db, service_id)

@router.post(
    "/business-types/",
    summary='Create New Business Type',
    response_model=BusinessTypeResponse,
    dependencies=[SuperAdminSession])
async def create_business_type(db: DBSession, business_type_create: BusinessTypeCreate):
    return await create_new_business_type(db, business_type_create)

@router.put(
    "/business-types/{business_type_id}",
    summary='Update Business Type',
    response_model=BusinessTypeResponse,
    dependencies=[SuperAdminSession])
async def update_business_type(db: DBSession, business_type_update: BusinessTypeUpdate, business_type_id: int):
    return await update_business_type_by_id(db, business_type_update, business_type_id)

@router.delete(
    "/business-types/{business_type_id}",
    summary='Delete Business Type',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def delete_business_type(db: DBSession, business_type_id: int):
    return await delete_business_type_by_id(db, business_type_id)

@router.post(
    "/business-types/{business_type_id}/filters/{filter_id}",
    summary='Attach Filter - Business Type',
    status_code=status.HTTP_201_CREATED,
    dependencies=[SuperAdminSession])
async def attach_filters_business_type(db: DBSession, business_type_id: int, filter_id: int):
    return await attach_filters_to_business_type(db, business_type_id, filter_id)

@router.delete(
    "/business-types/{business_type_id}/filters/{filter_id}",
    summary='Detach Filter - Business Type',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def detach_filters_business_type(db: DBSession, business_type_id: int, filter_id: int):
    return await detach_filters_from_business_type(db, business_type_id, filter_id)

@router.post(
    "/business-types/{business_type_id}/professions/{profession_id}",
    summary='Attach Profession - Business Type',
    status_code=status.HTTP_201_CREATED,
    dependencies=[SuperAdminSession])
async def attach_professions_business_type(db: DBSession, business_type_id: int, profession_id: int):
    return await attach_professions_to_business_type(db, business_type_id, profession_id)

@router.delete(
    "/business-types/{business_type_id}/professions/{profession_id}",
    summary='Detach Profession - Business Type',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def detach_professions_business_type(db:DBSession, business_type_id: int, profession_id: int):
    return await detach_professions_from_business_type(db, business_type_id, profession_id)
