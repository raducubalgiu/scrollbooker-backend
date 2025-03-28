from sqlalchemy.orm import joinedload
from app.core.crud_helpers import db_create, db_get_all, db_delete, db_update, db_insert_many_to_many, \
    db_remove_many_to_many
from app.core.dependencies import DBSession
from app.models import BusinessType, Service, Filter, SubFilter, Profession
from app.models.booking.nomenclature.business_type_filters import business_type_filters
from app.models.booking.nomenclature.business_type_professions import business_type_professions
from app.schema.booking.nomenclature.business_type import BusinessTypeCreate, BusinessTypeUpdate

async def get_all_business_types(db: DBSession, page: int, limit: int):
    return await db_get_all(db, model=BusinessType, page=page, limit=limit)

async def create_new_business_type(db: DBSession, business_type_create: BusinessTypeCreate):
    return await db_create(db, model=BusinessType, create_data=business_type_create)

async def delete_business_type_by_id(db: DBSession, business_type_id: int):
    return await db_delete(db, model=BusinessType, resource_id=business_type_id)

async def update_business_type_by_id(db: DBSession, business_type_update: BusinessTypeUpdate, business_type_id: int):
    return await db_update(db, model=BusinessType, update_data=business_type_update, resource_id=business_type_id)

async def get_all_business_types_with_services(db: DBSession, page: int, limit: int):
    return await db_get_all(db, model=BusinessType,
                joins=[
                    joinedload(BusinessType.services).load_only(Service.name),
                    joinedload(BusinessType.filters).load_only(Filter.name)
                    .joinedload(Filter.sub_filters).load_only(SubFilter.name)
                ], unique=True, page=page, limit=limit, order_by=["business_domain_id"])

async def get_all_business_types_with_professions(db: DBSession, page: int, limit: 10):
    return await db_get_all(db, model=BusinessType,
                joins=[joinedload(BusinessType.professions).load_only(Profession.name)],
                unique=True, page=page, limit=limit)

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