from fastapi import APIRouter
from starlette import status
from app.core.dependencies import DBSession, SuperAdminSession
from app.schema.booking.nomenclature.service_domain import ServiceDomainCreate, \
    ServiceDomainUpdate, ServiceDomainResponse, ServiceDomainWithServices
from app.service.booking.nomenclature.service_domain import get_all_service_domains, create_new_service_domain, \
    update_service_domain_by_id, delete_service_domain_by_id, get_all_service_domains_with_services

router = APIRouter(prefix="/service-domains", tags=["Service Domains"])

@router.get("/", response_model=list[ServiceDomainResponse])
async def get_service_domains(db: DBSession):
    return await get_all_service_domains(db)

@router.get("/with-services", response_model=list[ServiceDomainWithServices])
async def get_service_domains_with_services(db: DBSession):
    return await get_all_service_domains_with_services(db)

@router.post("/", response_model=ServiceDomainResponse, dependencies=[SuperAdminSession])
async def create_service_domain(db: DBSession, service_domain_create: ServiceDomainCreate):
    return await create_new_service_domain(db, service_domain_create)

@router.put("/{service_domain_id}", response_model=ServiceDomainResponse, dependencies=[SuperAdminSession])
async def update_service_domain(db: DBSession, service_domain_update: ServiceDomainUpdate, service_domain_id: int):
    return await update_service_domain_by_id(db, service_domain_update, service_domain_id)

@router.delete("/{service_domain_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[SuperAdminSession])
async def delete_service_domain(db: DBSession, service_domain_id: int):
    return await delete_service_domain_by_id(db, service_domain_id)