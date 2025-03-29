from sqlalchemy.orm import joinedload

from app.core.crud_helpers import db_create, db_update, db_delete, db_get_all, PaginatedResponse, db_get_all_paginate
from app.core.dependencies import DBSession
from app.schema.booking.nomenclature.service_domain import ServiceDomainCreate, ServiceDomainUpdate, \
    ServiceDomainWithServices
from app.models import ServiceDomain, Service

async def get_all_service_domains(db: DBSession):
    return await db_get_all(db, model=ServiceDomain)

async def get_all_service_domains_with_services(db: DBSession, page: int, limit: int):
    return await db_get_all_paginate(db, model=ServiceDomain, schema=ServiceDomainWithServices,
                page=page, limit=limit, unique=True, joins=[joinedload(ServiceDomain.services).load_only(Service.name)])

async def create_new_service_domain(db: DBSession, service_domain_create: ServiceDomainCreate):
    return await db_create(db, model=ServiceDomain, create_data=service_domain_create)

async def update_service_domain_by_id(db: DBSession, service_domain_update: ServiceDomainUpdate, service_domain_id: int):
    return await db_update(db, model=ServiceDomain, update_data=service_domain_update, resource_id=service_domain_id)

async def delete_service_domain_by_id(db: DBSession, service_domain_id: int):
    return await db_delete(db, model=ServiceDomain, resource_id=service_domain_id)