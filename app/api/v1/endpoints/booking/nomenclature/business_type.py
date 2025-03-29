from fastapi import APIRouter
from starlette import status

from app.core.crud_helpers import PaginatedResponse
from app.core.dependencies import DBSession, SuperAdminSession
from app.schema.booking.nomenclature.business_type import BusinessTypeResponse, BusinessTypeCreate, BusinessTypeUpdate, \
    BusinessTypeWithProfessionsResponse, BusinessTypeWithServicesAndFilters
from app.service.booking.nomenclature.business_type import create_new_business_type, \
    delete_business_type_by_id, update_business_type_by_id, get_all_business_types_with_services, \
    attach_filters_to_business_type, attach_professions_to_business_type, detach_professions_from_business_type, \
    detach_filters_from_business_type, get_all_business_types_with_professions

router = APIRouter(prefix="/business-types", tags=["Business Types"])

@router.get("/with-services-and-filters", response_model=PaginatedResponse[BusinessTypeWithServicesAndFilters])
async def get_business_types_with_services(db: DBSession, page: int, limit: int):
    return await get_all_business_types_with_services(db, page, limit)

@router.get("/with-professions", response_model=list[BusinessTypeWithProfessionsResponse])
async def get_business_types_with_professions(db: DBSession, page: int, limit: int):
    return await get_all_business_types_with_professions(db, page, limit)

@router.post("/", response_model=BusinessTypeResponse, dependencies=[SuperAdminSession])
async def create_business_type(db: DBSession, business_type_create: BusinessTypeCreate):
    return await create_new_business_type(db, business_type_create)

@router.put("/{business_type_id}", response_model=BusinessTypeResponse, dependencies=[SuperAdminSession])
async def update_business_type(db: DBSession, business_type_update: BusinessTypeUpdate, business_type_id: int):
    return await update_business_type_by_id(db, business_type_update, business_type_id)

@router.delete("/{business_type_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[SuperAdminSession])
async def delete_business_type(db: DBSession, business_type_id: int):
    return await delete_business_type_by_id(db, business_type_id)

@router.post("/{business_type_id}/filters/{filter_id}", status_code=status.HTTP_201_CREATED, dependencies=[SuperAdminSession])
async def attach_filters_business_type(db: DBSession, business_type_id: int, filter_id: int):
    return await attach_filters_to_business_type(db, business_type_id, filter_id)

@router.delete("/{business_type_id}/filters/{filter_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[SuperAdminSession])
async def detach_filters_business_type(db: DBSession, business_type_id: int, filter_id: int):
    return await detach_filters_from_business_type(db, business_type_id, filter_id)

@router.post("/{business_type_id}/professions/{profession_id}", status_code=status.HTTP_201_CREATED, dependencies=[SuperAdminSession])
async def attach_professions_business_type(db: DBSession, business_type_id: int, profession_id: int):
    return await attach_professions_to_business_type(db, business_type_id, profession_id)

@router.delete("/{business_type_id}/professions/{profession_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[SuperAdminSession])
async def detach_professions_business_type(db:DBSession, business_type_id: int, profession_id: int):
    return await detach_professions_from_business_type(db, business_type_id, profession_id)
