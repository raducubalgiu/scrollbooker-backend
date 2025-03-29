from app.core.crud_helpers import db_create, db_get_all, db_delete, db_update, db_get_all_paginate
from app.core.dependencies import DBSession
from app.models import BusinessDomain
from app.schema.booking.nomenclature.business_domain import BusinessDomainCreate, BusinessDomainUpdate

async def get_all_business_domain(db: DBSession):
    return await db_get_all(db, model=BusinessDomain)

async def create_new_business_domain(db: DBSession, business_domain_create: BusinessDomainCreate):
    return await db_create(db, model=BusinessDomain, create_data=business_domain_create)

async def update_business_domain_by_id(db: DBSession, business_domain_update: BusinessDomainUpdate, business_domain_id: int):
    return await db_update(db, model= BusinessDomain, update_data=business_domain_update, resource_id=business_domain_id)

async def delete_business_domain_by_id(db: DBSession, business_domain_id: int):
    return await db_delete(db, model=BusinessDomain, resource_id=business_domain_id)