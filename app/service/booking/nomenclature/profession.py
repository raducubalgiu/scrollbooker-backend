from sqlalchemy.orm import joinedload

from app.core.crud_helpers import db_create, db_update, db_delete, db_get_all_paginate
from app.core.dependencies import DBSession
from app.models import Profession, BusinessType
from app.schema.booking.nomenclature.profession import ProfessionCreate, ProfessionUpdate, \
    ProfessionWithBusinessTypesResponse

async def get_all_professions_with_business_types(db: DBSession, page: int, limit: int):
    return await db_get_all_paginate(db, model=Profession, schema=ProfessionWithBusinessTypesResponse,
                            joins=[joinedload(Profession.business_types).load_only(BusinessType.name)],
                            unique=True, page=page, limit=limit)

async def create_new_profession(db: DBSession, profession_create: ProfessionCreate):
    return await db_create(db, model=Profession, create_data=profession_create)

async def update_profession_by_id(db: DBSession, profession_update: ProfessionUpdate, profession_id: int):
    return await db_update(db, model=Profession, update_data=profession_update, resource_id=profession_id)

async def delete_profession_by_id(db: DBSession, profession_id: int):
    return await db_delete(db, model=Profession, resource_id=profession_id)