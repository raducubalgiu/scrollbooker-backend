from typing import Union

from fastapi import APIRouter
from starlette import status
from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession, Pagination
from backend.core.dependencies import SuperAdminSession
from backend.schema.nomenclature.service import ServiceResponse, ServiceCreate, ServiceUpdate
from backend.service.nomenclature.service import create_new_service, \
    delete_service_by_id, update_service_by_id, get_all_services, attach_services_to_business_type, \
    detach_services_from_business_type, get_services_by_business_id, get_services_by_service_domain_id, \
    get_services_by_business_type_id

router = APIRouter(tags=["Services"])

@router.get("/services",
    summary='List All Services',
    response_model=Union[PaginatedResponse[ServiceResponse],
    list[ServiceResponse]])
async def get_services(db: DBSession, pagination: Pagination):
    return await get_all_services(db, pagination)

@router.get(
    "/business-types/{business_type_id}/services",
    summary='List All Services Filtered By Business Type Id',
    response_model=Union[PaginatedResponse[ServiceResponse], list[ServiceResponse]])
async def get_services_by_business_type(db: DBSession, business_type_id: int):
    return await get_services_by_business_type_id(db, business_type_id)

@router.get("/service-domains/{service_domain_id}/services",
    summary='List All Services Filtered by Service Domain Id',
    response_model=Union[PaginatedResponse[ServiceResponse], list[ServiceResponse]])
async def get_services_by_service_domain(db: DBSession, service_domain_id: int, pagination: Pagination):
    return await get_services_by_service_domain_id(db, service_domain_id, pagination)

@router.get("/businesses/{business_id}/services",
    summary='List All Services Filtered by Business Id',
    response_model=list[ServiceResponse])
async def get_services_by_user(db: DBSession, business_id: int):
    return await get_services_by_business_id(db, business_id)

@router.post("/services",
    summary='Create New Service',
    response_model=ServiceResponse,
    dependencies=[SuperAdminSession])
async def create_service(db: DBSession, new_service: ServiceCreate):
    return await create_new_service(db, new_service)

@router.put("/services/{service_id}",
    summary='Update Service',
    response_model=ServiceResponse,
    dependencies=[SuperAdminSession])
async def update_service(db: DBSession, service_id: int, service_data: ServiceUpdate):
    return await update_service_by_id(db, service_id, service_data)

@router.delete("/services/{service_id}",
    summary='Delete Service',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def delete_service(db: DBSession, service_id: int):
    return await delete_service_by_id(db, service_id)

@router.post("/services/{service_id}/business-types/{business_type_id}",
    summary='Create Service - Business Type Relation',
    status_code=status.HTTP_201_CREATED)
async def attach_service_business_type(db: DBSession, service_id: int, business_type_id: int):
    return await attach_services_to_business_type(db, business_type_id, service_id)

@router.delete("/services/{service_id}/business-types/{business_type_id}",
    summary='Remove Service - Business Type Relation',
    status_code=status.HTTP_204_NO_CONTENT)
async def detach_service_business_type(db: DBSession, service_id: int, business_type_id: int):
    return await detach_services_from_business_type(db, business_type_id, service_id)