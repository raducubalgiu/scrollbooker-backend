from sqlalchemy.orm import joinedload

from core.crud_helpers import db_create, db_update, db_delete, db_get_all_paginate, db_get_one, db_get_all, \
    db_insert_many_to_many, db_remove_many_to_many
from core.dependencies import DBSession, Pagination
from models import Profession, BusinessType
from models.nomenclature.business_type_professions import business_type_professions
from schema.nomenclature.profession import ProfessionCreate, ProfessionUpdate, \
    ProfessionWithBusinessTypesResponse, ProfessionResponse

async def get_professions_by_business_type_id(db: DBSession, business_type_id: int):
    business_type = await db_get_one(db,
                            model=BusinessType,
                            filters={BusinessType.id: business_type_id},
                            joins=[joinedload(BusinessType.professions)])
    return business_type.professions

async def get_all_professions_with_business_types(db: DBSession, page: int, limit: int):
    return await db_get_all_paginate(db,
                                     model=Profession,
                                     schema=ProfessionWithBusinessTypesResponse,
                                     joins=[joinedload(Profession.business_types).load_only(BusinessType.name)],
                                     unique=True,
                                     page=page,
                                     limit=limit)

async def get_all_professions(db: DBSession, pagination: Pagination):
    return await db_get_all(db,
                            model=Profession,
                            schema=ProfessionResponse,
                            page=pagination.page,
                            limit=pagination.limit,
                            order_by="created_at",
                            descending=True)

async def create_new_profession(db: DBSession, profession_create: ProfessionCreate):
    return await db_create(db, model=Profession, create_data=profession_create)

async def update_profession_by_id(db: DBSession, profession_update: ProfessionUpdate, profession_id: int):
    return await db_update(db, model=Profession, update_data=profession_update, resource_id=profession_id)

async def delete_profession_by_id(db: DBSession, profession_id: int):
    return await db_delete(db, model=Profession, resource_id=profession_id)

async def attach_professions_to_business_type(db: DBSession, business_type_id: int, profession_id: int):
    return await db_insert_many_to_many(db,
                    model_one=BusinessType,
                    resource_one_id=business_type_id,
                    model_two=Profession,
                    resource_two_id=profession_id,
                    relation_table=business_type_professions)

async def detach_professions_from_business_type(db: DBSession, business_type_id: int, profession_id):
    return await db_remove_many_to_many(db,
                    model_one=BusinessType,
                    resource_one_id=business_type_id,
                    model_two=Profession,
                    resource_two_id=profession_id,
                    relation_table=business_type_professions)
