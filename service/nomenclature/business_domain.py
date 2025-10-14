from sqlalchemy.orm import joinedload

from core.crud_helpers import db_create, db_get_all, db_delete, db_update
from core.dependencies import DBSession, Pagination
from models import BusinessDomain
from schema.nomenclature.business_domain import BusinessDomainCreate, BusinessDomainUpdate, \
    BusinessDomainResponse, BusinessDomainsWithBusinessTypes


async def get_all_business_domain(db: DBSession, pagination: Pagination):
    return await db_get_all(db,
                            model=BusinessDomain,
                            schema=BusinessDomainResponse,
                            page=pagination.page,
                            limit=pagination.limit,
                            order_by="created_at",
                            descending=True)

async def get_all_business_domains_with_business_types(db: DBSession):
    return await db_get_all(db,
                            model=BusinessDomain,
                            schema=BusinessDomainsWithBusinessTypes,
                            joins=[joinedload(BusinessDomain.business_types)],
                            unique=True,
                            order_by="created_at",
                            descending=True)

async def create_new_business_domain(db: DBSession, business_domain_create: BusinessDomainCreate):
    return await db_create(db,
                           model=BusinessDomain,
                           create_data=business_domain_create)

async def update_business_domain_by_id(db: DBSession, business_domain_update: BusinessDomainUpdate, business_domain_id: int):
    return await db_update(db,
                           model= BusinessDomain,
                           update_data=business_domain_update,
                           resource_id=business_domain_id)

async def delete_business_domain_by_id(db: DBSession, business_domain_id: int):
    return await db_delete(db, model=BusinessDomain, resource_id=business_domain_id)