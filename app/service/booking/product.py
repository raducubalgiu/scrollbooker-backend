from fastapi import HTTPException
from starlette.requests import Request
from starlette import status
from app.core.crud_helpers import db_delete, db_get_all, db_update
from app.core.dependencies import DBSession, check_resource_ownership
from app.core.logger import logger
from app.models import Product, Schedule, product_sub_filters, business_services
from app.schema.booking.product import ProductCreateWithSubFilters, ProductUpdate, ProductCreate
from app.core.logger import logger
from sqlalchemy import insert,select

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

async def update_product_by_id(db: DBSession, product_id: int, product_update: ProductUpdate, request: Request):
    await check_resource_ownership(db, resource_model=Product, resource_id=product_id, request=request)

    return await db_update(db, model=Product, resource_id=product_id, update_data=product_update)

async def delete_product_by_id(db: DBSession, product_id: int, request: Request):
    await check_resource_ownership(db, Product, product_id, request)
    return await db_delete(db, model=Product, resource_id=product_id)













