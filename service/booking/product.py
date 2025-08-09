from fastapi import HTTPException
from fastapi.params import Query
from sqlalchemy.orm import joinedload
from starlette.requests import Request
from starlette import status
from core.crud_helpers import db_delete, db_get_all, db_update, db_get_one, PaginatedResponse
from core.dependencies import DBSession, check_resource_ownership, Pagination
from models import Product, Schedule, product_sub_filters, business_services, SubFilter
from schema.booking.product import ProductCreateWithSubFilters, ProductUpdate, ProductCreate, \
    ProductWithSubFiltersResponse, ProductResponse
from core.logger import logger
from sqlalchemy import insert, select, and_, desc, func


async def get_products_by_user_id(db: DBSession, user_id: int, pagination: Pagination):
    return await db_get_all(db,
                            model=Product,
                            filters={Product.user_id: user_id},
                            schema=ProductWithSubFiltersResponse,
                            page=pagination.page,
                            limit=pagination.limit,
                            unique=True,
                            joins=[joinedload(Product.sub_filters).joinedload(SubFilter.filter)])

async def get_products_by_user_id_and_service_id(
        db:DBSession,
        user_id: int,
        service_id: int,
        pagination: Pagination,
        employee_id: int = Query(None),
):
    owner_id = employee_id if employee_id is not None else user_id

    return await db_get_all(db,
                            model=Product,
                            schema=ProductResponse,
                            filters={
                                Product.user_id: owner_id,
                                Product.service_id: service_id
                            },
                            page=pagination.page,
                            limit=pagination.limit,
                            order_by="created_at",
                            descending=True)

async def get_product_by_id(db: DBSession, product_id: int):
    return await db_get_one(db, model=Product, filters={Product.id: product_id})

async def create_new_product(db: DBSession, product_with_sub_filters: ProductCreateWithSubFilters, request: Request):
    auth_user_id = request.state.user.get("id")
    has_schedules = await db_get_all(db, model=Schedule, filters={Schedule.user_id: auth_user_id})
    business_has_services_stmt = await db.execute(select(business_services).where(
        business_services.c.business_id == product_with_sub_filters.product.business_id #type: ignore
    ))
    business_has_services = business_has_services_stmt.scalars().unique().all()

    if not business_has_services:
        logger.error(f"Business: {product_with_sub_filters.product.business_id} has not services defined")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Business has not services defined')

    if not has_schedules:
        logger.error(f"User: {auth_user_id} has not schedules defined")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User has not schedules defined')
    try:
        if not product_with_sub_filters.sub_filters:
            logger.error(f"SubFilter is missing. Query param is empty, sub_filters: []")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Something went wrong')

        new_product = Product(**product_with_sub_filters.product.model_dump(), user_id=auth_user_id)
        db.add(new_product)
        await db.flush()

        sub_filters_stmt = insert(product_sub_filters).values([
            {"product_id": new_product.id, "sub_filter_id": sub_filter_id}
            for sub_filter_id in product_with_sub_filters.sub_filters
        ])

        await db.execute(sub_filters_stmt)
        await db.commit()
        return new_product

    except Exception as e:
        await db.rollback()

        logger.error(f"Product could not be saved. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')

async def update_by_id(db: DBSession, product_id: int, product_update: ProductUpdate, request: Request):
    await check_resource_ownership(db, resource_model=Product, resource_id=product_id, request=request)

    return await db_update(db, model=Product, resource_id=product_id, update_data=product_update)

async def delete_by_id(db: DBSession, product_id: int, request: Request):
    await check_resource_ownership(db, Product, product_id, request)
    return await db_delete(db, model=Product, resource_id=product_id)













