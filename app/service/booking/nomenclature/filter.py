from sqlalchemy.orm import joinedload

from app.core.crud_helpers import db_create, db_update, db_get_all_paginate, db_delete
from app.core.dependencies import DBSession
from app.schema.booking.nomenclature.filter import FilterCreate, FilterUpdate, FilterWithSubFiltersResponse
from app.models import Filter, SubFilter
from app.schema.booking.nomenclature.sub_filter import SubFilterResponse

async def get_filters_with_sub_filters(db: DBSession, page: int, limit: int):
    return await db_get_all_paginate(db, model=Filter, schema= FilterWithSubFiltersResponse,
            unique=True, page=page, limit=limit, joins=[joinedload(Filter.sub_filters).load_only(SubFilter.name)],
            order_by="created_at", descending=True)

async def get_sub_filters_by_filter_id(db: DBSession, filter_id: int, page: int, limit: int):
    return await db_get_all_paginate(db, model=SubFilter, schema=SubFilterResponse, page=page, limit=limit,
           filters={SubFilter.filter_id: filter_id}, order_by="created_at", descending=True)

async def create_new_filter(db: DBSession, filter_create: FilterCreate):
    return await db_create(db, model=Filter, create_data=filter_create)

async def update_filter_by_id(db: DBSession, filter_update: FilterUpdate, filter_id: int):
    return await db_update(db, model=Filter, update_data=filter_update, resource_id=filter_id)

async def delete_filter_by_id(db: DBSession, filter_id: int):
    return await db_delete(db, model=Filter, resource_id=filter_id)