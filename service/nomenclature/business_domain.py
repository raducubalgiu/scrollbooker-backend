from backend.core.crud_helpers import db_create, db_get_all, db_delete, db_update
from backend.core.dependencies import DBSession, Pagination
from backend.models import BusinessDomain
from backend.schema.nomenclature.business_domain import BusinessDomainCreate, BusinessDomainUpdate, \
    BusinessDomainResponse

async def get_all_business_domain(db: DBSession, pagination: Pagination):
    return await db_get_all(db,
                            model=BusinessDomain,
                            schema=BusinessDomainResponse,
                            page=pagination.page,
                            limit=pagination.limit,
                            order_by="created_at",
                            descending=True)

async def create_new_business_domain(db: DBSession, business_domain_create: BusinessDomainCreate):
    return await db_create(db, model=BusinessDomain, create_data=business_domain_create)

async def update_business_domain_by_id(db: DBSession, business_domain_update: BusinessDomainUpdate, business_domain_id: int):
    return await db_update(db, model= BusinessDomain, update_data=business_domain_update, resource_id=business_domain_id)

async def delete_business_domain_by_id(db: DBSession, business_domain_id: int):
    return await db_delete(db, model=BusinessDomain, resource_id=business_domain_id)