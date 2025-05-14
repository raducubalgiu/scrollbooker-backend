from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload

from backend.core.dependencies import DBSession, Pagination
from backend.models import Service, BusinessType, Business, User
from backend.schema.booking.nomenclature.service import ServiceCreate, ServiceUpdate, ServiceResponse
from backend.core.crud_helpers import db_create, db_delete, db_update, db_get_all, db_insert_many_to_many, \
    db_remove_many_to_many, db_get_one
from backend.models.booking.nomenclature.service_business_types import service_business_types

async def get_all_services(db: DBSession, pagination: Pagination):
    return await db_get_all(db,
        model=Service, schema=ServiceResponse, page=pagination.page, limit=pagination.limit, order_by="created_at", descending=True)

async def get_services_by_business_type_id(db: DBSession, business_type_id: int):
    business_type = await db_get_one(db,
                                     model=BusinessType,
                                     filters={BusinessType.id: business_type_id},
                                     joins=[joinedload(BusinessType.services)])
    return business_type.services

async def get_services_by_service_domain_id(db: DBSession, service_domain_id: int, pagination: Pagination):
    return await db_get_all(db, model=Service, schema=ServiceResponse, filters={Service.service_domain_id: service_domain_id}, page=pagination.page, limit=pagination.limit)

async def get_services_by_user_id(db: DBSession, user_id: int):
    business_result = await db.execute(
        select(Business)
        .join(User, User.id == user_id) #type: ignore
        .where(or_(
            User.employee_business_id == Business.id,
            Business.owner_id == User.id
        ))
        .options(joinedload(Business.services))
    )
    business = business_result.scalars().first()
    return business.services

async def create_new_service(db: DBSession, new_service: ServiceCreate):
    return await db_create(db, model=Service, create_data=new_service)

async def update_service_by_id(db: DBSession, service_id: int, service_data: ServiceUpdate):
    return await db_update(db, resource_id=service_id, model=Service, update_data=service_data)

async def delete_service_by_id(db: DBSession, service_id: int):
    return await db_delete(db, model=Service, resource_id=service_id)

async def attach_services_to_business_type(db: DBSession, business_type_id: int, service_id: int):
    return await db_insert_many_to_many(db,
        model_one=Service,
        resource_one_id=service_id,
        model_two=BusinessType,
        resource_two_id=business_type_id,
        relation_table=service_business_types
    )

async def detach_services_from_business_type(db: DBSession, business_type_id: int, service_id: int):
    return await db_remove_many_to_many(db,
        model_one=Service,
        resource_one_id=service_id,
        model_two=BusinessType,
        resource_two_id=business_type_id,
        relation_table=service_business_types
    )


