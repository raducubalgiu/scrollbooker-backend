from sqlalchemy.orm import joinedload
from backend.core.crud_helpers import db_create, db_delete, db_update, db_insert_many_to_many, \
    db_remove_many_to_many, db_get_one, db_get_all
from backend.core.dependencies import DBSession, Pagination
from backend.models import BusinessType, Service, Filter, Profession
from backend.models.nomenclature.business_type_filters import business_type_filters
from backend.schema.nomenclature.business_type import BusinessTypeCreate, BusinessTypeUpdate, BusinessTypeResponse

async def get_all_business_types(db: DBSession, pagination: Pagination):
    return await db_get_all(db,
                            model=BusinessType,
                            schema=BusinessTypeResponse,
                            page=pagination.page,
                            limit=pagination.limit)

async def get_business_types_by_profession_id(db: DBSession, profession_id: int, pagination: Pagination):
    profession = await db_get_one(db,
                                  model=Profession,
                                  filters={Profession.id: profession_id},
                                  joins=[joinedload(Profession.business_types)])
    return profession.business_types

async def get_business_types_by_filter_id(db: DBSession, filter_id: int):
    filter_data = await db_get_one(db,
                                  model=Filter,
                                  filters={Filter.id: filter_id},
                                  joins=[joinedload(Filter.business_types)])
    return filter_data.business_types

async def get_business_types_by_business_domain_id(db: DBSession, business_domain_id: int, pagination: Pagination):
    return await db_get_all(db,
                            model=BusinessType,
                            schema=BusinessTypeResponse,
                            filters={BusinessType.business_domain_id: business_domain_id},
                            page=pagination.page,
                            limit=pagination.limit)

async def get_business_types_by_service_id(db: DBSession, service_id: int):
    service = await db_get_one(db, model=Service, filters={Service.id: service_id}, joins=[joinedload(Service.business_types)])
    return service.business_types

async def create_new_business_type(db: DBSession, business_type_create: BusinessTypeCreate):
    return await db_create(db, model=BusinessType, create_data=business_type_create)

async def delete_business_type_by_id(db: DBSession, business_type_id: int):
    return await db_delete(db, model=BusinessType, resource_id=business_type_id)

async def update_business_type_by_id(db: DBSession, business_type_update: BusinessTypeUpdate, business_type_id: int):
    return await db_update(db, model=BusinessType, update_data=business_type_update, resource_id=business_type_id)
