from typing import Union
from fastapi import APIRouter
from starlette import status
from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession, SuperAdminSession, Pagination
from backend.schema.nomenclature.business_type import BusinessTypeResponse, BusinessTypeCreate, BusinessTypeUpdate
from backend.service.nomenclature.business_type import create_new_business_type, \
    delete_business_type_by_id, update_business_type_by_id, get_business_types_by_business_domain_id, \
    get_business_types_by_service_id, get_all_business_types, get_business_types_by_profession_id, get_business_types_by_filter_id

router = APIRouter(tags=["Business Types"])

@router.get("/business-types",
    summary='List All Business Types',
    response_model=Union[PaginatedResponse[BusinessTypeResponse], list[BusinessTypeResponse]])
async def get_business_types(db: DBSession, pagination: Pagination):
    return await get_all_business_types(db, pagination)

@router.get("/professions/{profession_id}/business-types",
    summary='List All Business Types Filtered By Profession Id',
    response_model=list[BusinessTypeResponse])
async def get_business_types_by_profession(db: DBSession, profession_id: int, pagination: Pagination):
    return await get_business_types_by_profession_id(db, profession_id, pagination)

@router.get("/business-domains/{business_domain_id}/business-types",
    summary='List All Business Types Filtered By Business Domain Id',
    response_model=Union[PaginatedResponse[BusinessTypeResponse], list[BusinessTypeResponse]])
async def get_business_types_by_business_domain(db: DBSession, business_domain_id: int, pagination: Pagination):
    return await get_business_types_by_business_domain_id(db, business_domain_id, pagination)

@router.get("/services/{service_id}/business-types",
    summary='List All Business Types Filtered By Service Id',
    response_model=list[BusinessTypeResponse])
async def get_business_types_by_service(db: DBSession, service_id: int):
    return await get_business_types_by_service_id(db, service_id)

@router.get("/filters/{filter_id}/business-types",
    summary='List All Business Types Filtered By Filter Id',
    response_model=list[BusinessTypeResponse])
async def get_business_types_by_filter(db: DBSession, filter_id: int):
    return await get_business_types_by_filter_id(db, filter_id)

@router.post("/business-types/",
    summary='Create New Business Type',
    response_model=BusinessTypeResponse,
    dependencies=[SuperAdminSession])
async def create_business_type(db: DBSession, business_type_create: BusinessTypeCreate):
    return await create_new_business_type(db, business_type_create)

@router.put("/business-types/{business_type_id}",
    summary='Update Business Type',
    response_model=BusinessTypeResponse,
    dependencies=[SuperAdminSession])
async def update_business_type(db: DBSession, business_type_update: BusinessTypeUpdate, business_type_id: int):
    return await update_business_type_by_id(db, business_type_update, business_type_id)

@router.delete("/business-types/{business_type_id}",
    summary='Delete Business Type',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def delete_business_type(db: DBSession, business_type_id: int):
    return await delete_business_type_by_id(db, business_type_id)

