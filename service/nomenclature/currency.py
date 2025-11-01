from typing import List

from fastapi import HTTPException, Request, Response, status
from sqlalchemy import select, and_, delete, insert
from sqlalchemy.orm import selectinload

from core.crud_helpers import db_create, db_get_all, db_update
from core.dependencies import DBSession, Pagination
from core.enums.registration_step_enum import RegistrationStepEnum
from models import Currency, User, UserCurrency, Product
from schema.nomenclature.currency import CurrencyCreate, CurrencyResponse, CurrencyUpdate, UserCurrenciesUpdate
from core.logger import logger
from schema.user.user import UserAuthStateResponse

async def get_all_currencies(db: DBSession, pagination: Pagination):
    return await db_get_all(db, model=Currency, schema=CurrencyResponse, page=pagination.page, limit=pagination.limit, order_by="created_at", descending=True)

async def create_new_currency(db: DBSession, currency_create: CurrencyCreate):
    return await db_create(db, model=Currency, create_data=currency_create)

async def update_currency_by_id(db: DBSession, currency_id: int, currency_update: CurrencyUpdate):
    return await db_update(db, model=Currency, resource_id=currency_id, update_data=currency_update)

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

async def update_currencies_by_user(
        db: DBSession,
        currency_update: UserCurrenciesUpdate,
        request: Request
) -> List[CurrencyResponse]:
    auth_user_id = request.state.user.get("id")

    async with db.begin():
        result = await db.execute(
            select(UserCurrency.currency_id)
            .where(and_(UserCurrency.user_id == auth_user_id))
        )

        existing_currencies = set(row[0] for row in result.fetchall())

        incoming_currencies = set(currency_update.currency_ids)
        to_add = incoming_currencies - existing_currencies
        to_remove = existing_currencies - incoming_currencies

        if to_remove:
            result = await db.execute(
                select(Product.currency_id)
                .where(and_(
                    Product.user_id == auth_user_id,
                    Product.currency_id.in_(to_remove)
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
                delete(UserCurrency).where(
                    and_(
                        UserCurrency.user_id == auth_user_id,
                        UserCurrency.currency_id.in_(to_remove)
                    )
                )
            )

        if to_add:
            await db.execute(
                insert(UserCurrency),
                [{"user_id": auth_user_id, "currency_id": currency_id} for currency_id in to_add]
            )

        new_currencies = await get_currencies_by_user_id(db, auth_user_id)
        return new_currencies