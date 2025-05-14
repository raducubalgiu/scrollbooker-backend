from typing import Union

from fastapi import APIRouter
from starlette import status

from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession, SuperAdminSession, Pagination
from backend.schema.booking.nomenclature.service_domain import ServiceDomainCreate, \
    ServiceDomainUpdate, ServiceDomainResponse
from backend.service.booking.nomenclature.service_domain import get_all_service_domains, create_new_service_domain, \
    update_service_domain_by_id, delete_service_domain_by_id

router = APIRouter(prefix="/service-domains", tags=["Service Domains"])

@router.get("/",
    summary='List All Service Domains',
    response_model=Union[PaginatedResponse[ServiceDomainResponse], list[ServiceDomainResponse]])
async def get_service_domains(db: DBSession, pagination: Pagination):
    return await get_all_service_domains(db, pagination)

@router.post("/",
    summary='Create New Service Domain',
    response_model=ServiceDomainResponse,
    dependencies=[SuperAdminSession])
async def create_service_domain(db: DBSession, service_domain_create: ServiceDomainCreate):
    return await create_new_service_domain(db, service_domain_create)

@router.put("/{service_domain_id}",
    summary='Update Service Domain',
    response_model=ServiceDomainResponse,
    dependencies=[SuperAdminSession])
async def update_service_domain(db: DBSession, service_domain_update: ServiceDomainUpdate, service_domain_id: int):
    return await update_service_domain_by_id(db, service_domain_update, service_domain_id)

@router.delete("/{service_domain_id}",
    summary='Delete Service Domain',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def delete_service_domain(db: DBSession, service_domain_id: int):
    return await delete_service_domain_by_id(db, service_domain_id)