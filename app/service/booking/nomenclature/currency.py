from fastapi import HTTPException
from starlette import status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.crud_helpers import db_create, db_get_all, db_update
from app.core.dependencies import DBSession, Pagination
from app.models import Currency, User, UserCurrency
from app.schema.booking.nomenclature.currency import CurrencyCreate, CurrencyResponse, CurrencyUpdate


async def get_all_currencies(db: DBSession, pagination: Pagination):
    return await db_get_all(db, model=Currency, schema=CurrencyResponse, page=pagination.page, limit=pagination.limit, order_by="created_at", descending=True)

async def get_currencies_by_user_id(db: DBSession, user_id: int):
    user_result = await db.execute(
        select(User).options(
            selectinload(User.currencies_assoc).selectinload(UserCurrency.currency)
        )
        .where(User.id == user_id) #type: ignore
    )
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    currencies = [assoc.currency for assoc in user.currencies_assoc if assoc.active]
    return currencies

async def create_new_currency(db: DBSession, currency_create: CurrencyCreate):
    return await db_create(db, model=Currency, create_data=currency_create)

async def update_currency_by_id(db: DBSession, currency_id: int, currency_update: CurrencyUpdate):
    return await db_update(db, model=Currency, resource_id=currency_id, update_data=currency_update)
