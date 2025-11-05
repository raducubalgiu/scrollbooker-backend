from typing import Union, List

from fastapi import APIRouter, status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, SuperAdminSession, Pagination
from schema.nomenclature.service_domain import ServiceDomainCreate, \
    ServiceDomainUpdate, ServiceDomainResponse
from service.nomenclature.service_domain import get_all_service_domains, create_new_service_domain, \
    update_service_domain_by_id, delete_service_domain_by_id, get_service_domains_by_business_domain_id

router = APIRouter(tags=["Service Domains"])

@router.get("/service-domains",
    summary='List All Service Domains',
    response_model=Union[PaginatedResponse[ServiceDomainResponse], List[ServiceDomainResponse]])
async def get_service_domains(db: DBSession, pagination: Pagination):
    return await get_all_service_domains(db, pagination)

@router.get("/business_domains/{business_domain_id}/service-domains",
    summary='List All Service Domains Filtered by Business Domain Id',
    response_model=Union[PaginatedResponse[ServiceDomainResponse], List[ServiceDomainResponse]])
async def get_service_domains_by_business_domain(db: DBSession, business_domain_id: int, pagination: Pagination):
    return await get_service_domains_by_business_domain_id(db, business_domain_id, pagination)

@router.post("/service-domains",
    summary='Create New Service Domain',
    response_model=ServiceDomainResponse,
    dependencies=[SuperAdminSession])
async def create_service_domain(db: DBSession, service_domain_create: ServiceDomainCreate):
    return await create_new_service_domain(db, service_domain_create)

@router.put("/service-domains/{service_domain_id}",
    summary='Update Service Domain',
    response_model=ServiceDomainResponse,
    dependencies=[SuperAdminSession])
async def update_service_domain(db: DBSession, service_domain_update: ServiceDomainUpdate, service_domain_id: int):
    return await update_service_domain_by_id(db, service_domain_update, service_domain_id)

@router.delete("/service-domains{service_domain_id}",
    summary='Delete Service Domain',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def delete_service_domain(db: DBSession, service_domain_id: int):
    return await delete_service_domain_by_id(db, service_domain_id)