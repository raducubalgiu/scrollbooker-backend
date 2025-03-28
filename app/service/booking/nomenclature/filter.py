from sqlalchemy.orm import joinedload

from app.core.crud_helpers import db_create, db_get_all, db_update
from app.core.dependencies import DBSession
from app.schema.booking.nomenclature.filter import FilterCreate, FilterUpdate
from app.models import Filter, SubFilter

async def get_filters_with_sub_filters(db: DBSession):
    return await db_get_all(db, model=Filter, unique=True, joins=[
        joinedload(Filter.sub_filters).load_only(SubFilter.name)
    ])

async def create_new_filter(db: DBSession, filter_create: FilterCreate):
    return await db_create(db, model=Filter, create_data=filter_create)

async def update_filter_by_id(db: DBSession, filter_update: FilterUpdate, filter_id: int):
    return await db_update(db, model=Filter, update_data=filter_update, resource_id=filter_id)