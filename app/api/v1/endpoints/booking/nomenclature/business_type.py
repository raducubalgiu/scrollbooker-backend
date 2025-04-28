from fastapi import APIRouter
from starlette import status

from app.core.crud_helpers import PaginatedResponse
from app.core.dependencies import DBSession, SuperAdminSession
from app.schema.booking.nomenclature.business_type import BusinessTypeResponse, BusinessTypeCreate, BusinessTypeUpdate, \
    BusinessTypeWithProfessionsResponse, BusinessTypeWithServicesAndFiltersResponse
from app.schema.booking.nomenclature.filter import FilterResponse, FilterWithSubFiltersResponse
from app.schema.booking.nomenclature.profession import ProfessionResponse
from app.schema.booking.nomenclature.service import ServiceResponse
from app.service.booking.nomenclature.business_type import create_new_business_type, \
    delete_business_type_by_id, update_business_type_by_id, \
    attach_filters_to_business_type, attach_professions_to_business_type, detach_professions_from_business_type, \
    detach_filters_from_business_type, get_all_business_types_with_professions, \
    get_business_type_filters_and_sub_filters_by_id, get_all_business_type_with_services, \
    get_professions_by_business_type_id, get_services_by_business_type_id

router = APIRouter(prefix="/business-types", tags=["Business Types"])

@router.get("/{business_type_id}/services", response_model=list[ServiceResponse])
async def get_business_type_services(db: DBSession, business_type_id: int):
    return await get_services_by_business_type_id(db, business_type_id)

@router.get("/{business_type_id}/professions", response_model=list[ProfessionResponse])
async def get_business_type_professions(db: DBSession, business_type_id: int):
    return await get_professions_by_business_type_id(db, business_type_id)

@router.get("/with-services-and-filters", response_model=PaginatedResponse[BusinessTypeWithServicesAndFiltersResponse])
async def get_business_types_with_services(db: DBSession, page: int, limit: int):
    return await get_all_business_type_with_services(db, page, limit)

@router.get("/with-professions", response_model=PaginatedResponse[BusinessTypeWithProfessionsResponse])
async def get_business_types_with_professions(db: DBSession, page: int, limit: int):
    return await get_all_business_types_with_professions(db, page, limit)

@router.get("/{business_type_id}/filters", response_model=list[FilterWithSubFiltersResponse])
async def get_business_type_filters_and_sub_filters(db: DBSession, business_type_id: int):
    return await get_business_type_filters_and_sub_filters_by_id(db, business_type_id)

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
