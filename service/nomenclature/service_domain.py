from typing import Union, List

from core.crud_helpers import db_create, db_update, db_delete, db_get_all, PaginatedResponse
from core.dependencies import DBSession, Pagination
from schema.nomenclature.service_domain import ServiceDomainCreate, ServiceDomainUpdate, \
    ServiceDomainResponse
from models import ServiceDomain

async def get_all_service_domains(
        db: DBSession,
        pagination: Pagination
) -> Union[PaginatedResponse[ServiceDomainResponse], List[ServiceDomainResponse]]:
    return await db_get_all(
        db=db,
        model=ServiceDomain,
        schema=ServiceDomainResponse,
        page=pagination.page,
        limit=pagination.limit,
        order_by="created_at",
        descending=True
    )

async def get_service_domains_by_business_domain_id(
        db: DBSession,
        business_domain_id: int,
        pagination: Pagination
) -> Union[PaginatedResponse[ServiceDomainResponse], List[ServiceDomainResponse]]:
    return await db_get_all(
        db=db,
        model=ServiceDomain,
        schema=ServiceDomainResponse,
        filters={ ServiceDomain.business_domain_id: business_domain_id },
        page=pagination.page,
        limit=pagination.limit,
        order_by="created_at",
        descending=True
    )

async def create_new_service_domain(
        db: DBSession,
        service_domain_create: ServiceDomainCreate
):
    return await db_create(
        db=db,
        model=ServiceDomain,
        create_data=service_domain_create
    )

async def update_service_domain_by_id(
        db: DBSession,
        service_domain_update: ServiceDomainUpdate,
        service_domain_id: int
):
    return await db_update(
        db=db,
        model=ServiceDomain,
        update_data=service_domain_update,
        resource_id=service_domain_id
    )

async def delete_service_domain_by_id(
        db: DBSession,
        service_domain_id: int
):
    return await db_delete(db, model=ServiceDomain, resource_id=service_domain_id)