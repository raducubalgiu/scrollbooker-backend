from fastapi import HTTPException
from starlette.requests import Request
from starlette import status
from sqlalchemy import select, and_
from backend.core.crud_helpers import db_create
from backend.core.dependencies import DBSession
from backend.models import UserCurrency, User
from backend.schema.user.user_currency import UserCurrencyCreate, UserCurrencyUpdate
from backend.core.logger import logger

async def create_new_user_currency(db: DBSession, user_currency_create: UserCurrencyCreate, request: Request):
    auth_user_id = request.state.user.get("id")
    user = await db.get(User, user_currency_create.user_id)

    if user.id != auth_user_id:
        logger.error(f"Authenticated User ID: {auth_user_id} attempted to attach currency ID: {user_currency_create.currency_id} to user ID: {user_currency_create.user_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='You do not have permissions to perform this action')

    user_currency_result = await db.execute(
        select(UserCurrency)
        .where(and_(
            UserCurrency.user_id == user_currency_create.user_id,
            UserCurrency.currency_id == user_currency_create.currency_id,
            UserCurrency.active == True
        ))
    )
    user_currency = user_currency_result.scalars().first()

    if user_currency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Currency already Present')

    return await db_create(db, model=UserCurrency, create_data=user_currency_create)

async def delete_new_user_currency(db: DBSession, user_currency_update: UserCurrencyUpdate, request: Request):
    auth_user_id = request.state.user.get("id")
    user = await db.get(User, user_currency_update.user_id)

    if user.id != auth_user_id:
        logger.error(f"Authenticated User ID: {auth_user_id} attempted to detach currency ID: {user_currency_update.currency_id} from user ID: {user_currency_update.user_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='You do not have permissions to perform this action')

    user_currency_result = await db.execute(
        select(UserCurrency)
        .where(and_(
            UserCurrency.user_id == user_currency_update.user_id,
            UserCurrency.currency_id == user_currency_update.currency_id,
            UserCurrency.active == True
        ))
    )
    user_currency = user_currency_result.scalars().first()

    if not user_currency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='UserCurrency Not Found')

    user_currency.active = False
    await db.commit()