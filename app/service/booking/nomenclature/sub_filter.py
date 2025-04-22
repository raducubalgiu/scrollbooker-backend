from app.core.crud_helpers import db_create, db_update, db_delete
from app.core.dependencies import DBSession
from app.schema.booking.nomenclature.sub_filter import SubFilterCreate, SubFilterUpdate
from app.models import SubFilter

async def create_new_sub_filter(db: DBSession, sub_filter_create: SubFilterCreate):
    return await db_create(db, model=SubFilter, create_data=sub_filter_create)

async def update_sub_filter_by_id(db: DBSession, sub_filter_update:SubFilterUpdate, sub_filter_id: int):
    return await db_update(db, model=SubFilter, update_data=sub_filter_update, resource_id=sub_filter_id)

async def delete_sub_filters_by_id(db: DBSession, sub_filter_id: int):
    return await db_delete(db, model=SubFilter, resource_id=sub_filter_id)