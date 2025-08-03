from starlette import status
from sqlalchemy import select, or_, and_, delete, insert, false, distinct
from sqlalchemy.orm import joinedload
from starlette.exceptions import HTTPException
from starlette.requests import Request

from core.dependencies import DBSession, Pagination
from core.enums.registration_step_enum import RegistrationStepEnum
from models import Service, BusinessType, Business, User, business_services, Product
from schema.nomenclature.service import ServiceCreate, ServiceUpdate, ServiceResponse, ServiceIdsUpdate
from core.crud_helpers import db_create, db_delete, db_update, db_get_all, db_insert_many_to_many, \
    db_remove_many_to_many, db_get_one
from models.nomenclature.service_business_types import service_business_types
from core.logger import logger
from schema.user.user import UserAuthStateResponse


async def get_all_services(db: DBSession, pagination: Pagination):
    return await db_get_all(db,
        model=Service, schema=ServiceResponse, page=pagination.page, limit=pagination.limit, order_by="created_at", descending=True)

async def get_services_by_business_type_id(db: DBSession, business_type_id: int):
    business_type = await db_get_one(db,
                                     model=BusinessType,
                                     filters={BusinessType.id: business_type_id},
                                     joins=[joinedload(BusinessType.services)])
    return business_type.services

async def get_services_by_service_domain_id(db: DBSession, service_domain_id: int, pagination: Pagination):
    return await db_get_all(db, model=Service, schema=ServiceResponse, filters={Service.service_domain_id: service_domain_id}, page=pagination.page, limit=pagination.limit)

async def get_services_by_business_id(db: DBSession, business_id: int):
    stmt = (
        select(Business)
        .where(and_(Business.id == business_id))
        .options(
            joinedload(Business.services)
        )
    )
    result = await db.execute(stmt)
    business = result.scalars().first()

    return business.services

async def get_services_by_user_id(db: DBSession, user_id: int):
    stmt = (
        select(Service)
        .join(business_services, business_services.c.service_id == Service.id)
        .join(Business, Business.id == business_services.c.business_id)
        .join(User, or_(
            User.id == Business.owner_id,
            User.employee_business_id == Business.id
        ))
        .join(Product, Product.service_id == Service.id)
        .where(User.id == user_id)
        .distinct()
    )
    result = await db.execute(stmt)
    services = result.scalars().all()

    return services

async def create_new_service(db: DBSession, new_service: ServiceCreate):
    return await db_create(db, model=Service, create_data=new_service)

async def update_service_by_id(db: DBSession, service_id: int, service_data: ServiceUpdate):
    return await db_update(db, resource_id=service_id, model=Service, update_data=service_data)

async def delete_service_by_id(db: DBSession, service_id: int):
    return await db_delete(db, model=Service, resource_id=service_id)

async def update_services_by_business_id(db: DBSession, services_update: ServiceIdsUpdate, request: Request):
    auth_user_id = request.state.user.get("id")

    try:
        business_query = await db.execute(
            select(Business.id, Business.owner_id)
            .where(and_(
                User.id == auth_user_id,
                or_(
                    Business.owner_id == auth_user_id,
                    Business.id == User.employee_business_id
                )
            )
        )
                                          )
        business = business_query.unique().mappings().first()
        business_id, owner_id = business["id"], business["owner_id"]

        result = await db.execute(
            select(business_services.c.service_id)
            .where(and_(business_services.c.business_id == business_id))
        )

        existing_services = set(row[0] for row in result.fetchall())
        incoming_services = set(services_update.service_ids)
        to_add = incoming_services - existing_services
        to_remove = existing_services - incoming_services

        if to_remove:
            result = await db.execute(
                select(Product.service_id)
                .where(and_(
                    Product.business_id == business_id,
                    Product.service_id.in_(to_remove)
                ))
            )
            conflicting_services = result.scalars().all()

            if conflicting_services:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete services because has associated products"
                )

        if to_remove:
            await db.execute(
                delete(business_services).where(and_(
                    business_services.c.business_id == business_id,
                    business_services.c.service_id.in_(to_remove)
                ))
            )

        if to_add:
            await db.execute(
                insert(business_services),
                [
                    {
                        "business_id": business_id,
                        "service_id": service_id
                    } for service_id in to_add
                ]
            )

        owner = await db.get(User, owner_id)

        if owner.registration_step is RegistrationStepEnum.COLLECT_BUSINESS_SERVICES:
            owner.registration_step = RegistrationStepEnum.COLLECT_BUSINESS_SCHEDULES

        db.add(owner)

        await db.commit()
        await db.refresh(owner)

        return UserAuthStateResponse(
            is_validated=owner.is_validated,
            registration_step=owner.registration_step
        )

    except Exception as e:
        await db.rollback()

        logger.error(f"Business services could not be updated. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )


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


