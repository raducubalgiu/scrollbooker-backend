from app.core.dependencies import DBSession
from app.models import Service, BusinessType
from app.schema.booking.nomenclature.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.core.crud_helpers import db_create, db_delete, db_update, db_get_all_paginate, db_insert_many_to_many, \
    db_remove_many_to_many
from app.models.booking.nomenclature.service_business_types import service_business_types

async def get_all_services(db: DBSession, page: int, limit: int):
    return await db_get_all_paginate(db,
        model=Service, schema=ServiceResponse, page=page, limit=limit, order_by="created_at", descending=True)

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


