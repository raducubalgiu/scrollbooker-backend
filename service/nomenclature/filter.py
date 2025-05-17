from sqlalchemy.orm import joinedload

from backend.core.crud_helpers import db_create, db_update, db_get_all_paginate, db_delete, db_get_one, \
    db_insert_many_to_many, db_remove_many_to_many, db_get_all
from backend.core.dependencies import DBSession
from backend.models.nomenclature.business_type_filters import business_type_filters
from backend.schema.nomenclature.filter import FilterCreate, FilterUpdate, FilterWithSubFiltersResponse
from backend.models import Filter, BusinessType

async def get_all_filters(db: DBSession, page: int, limit: int):
    return await db_get_all(db,
                             model=Filter,
                             schema= FilterWithSubFiltersResponse,
                             unique=True,
                             page=page,
                             limit=limit,
                             order_by="created_at",
                             descending=True)

async def get_filters_by_business_type_id(db: DBSession, business_type_id: int):
    business_type = await db_get_one(db,
                                     model=BusinessType,
                                     filters={BusinessType.id: business_type_id},
                                     joins=[joinedload(BusinessType.filters)])
    return business_type.filters

async def create_new_filter(db: DBSession, filter_create: FilterCreate):
    return await db_create(db, model=Filter, create_data=filter_create)

async def update_filter_by_id(db: DBSession, filter_update: FilterUpdate, filter_id: int):
    return await db_update(db, model=Filter, update_data=filter_update, resource_id=filter_id)

async def delete_filter_by_id(db: DBSession, filter_id: int):
    return await db_delete(db, model=Filter, resource_id=filter_id)

async def attach_filters_to_business_type(db: DBSession, business_type_id: int, filter_id: int):
    return await db_insert_many_to_many(db,
                    model_one=BusinessType,
                    resource_one_id=business_type_id,
                    model_two=Filter,
                    resource_two_id=filter_id,
                    relation_table=business_type_filters)

async def detach_filters_from_business_type(db: DBSession, business_type_id: int, filter_id: int):
    return await db_remove_many_to_many(db,
                    model_one=BusinessType,
                    resource_one_id=business_type_id,
                    model_two=Filter,
                    resource_two_id=filter_id,
                    relation_table=business_type_filters)