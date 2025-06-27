from core.crud_helpers import db_create, db_update, db_delete, db_get_all
from core.dependencies import DBSession, Pagination
from schema.nomenclature.sub_filter import SubFilterCreate, SubFilterUpdate, SubFilterResponse
from models import SubFilter

async def get_sub_filters_by_filter_id(db: DBSession, filter_id: int, pagination: Pagination):
    return await db_get_all(db,
                             model=SubFilter,
                             schema=SubFilterResponse,
                             filters={SubFilter.filter_id: filter_id},
                             page=pagination.page,
                             limit=pagination.limit,
                             order_by="created_at",
                             descending=True)

async def create_new_sub_filter(db: DBSession, sub_filter_create: SubFilterCreate):
    return await db_create(db, model=SubFilter, create_data=sub_filter_create)

async def update_sub_filter_by_id(db: DBSession, sub_filter_update:SubFilterUpdate, sub_filter_id: int):
    return await db_update(db, model=SubFilter, update_data=sub_filter_update, resource_id=sub_filter_id)

async def delete_sub_filters_by_id(db: DBSession, sub_filter_id: int):
    return await db_delete(db, model=SubFilter, resource_id=sub_filter_id)