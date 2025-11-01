from typing import Union, List
from fastapi import APIRouter, Request

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, SuperAdminSession, Pagination
from schema.nomenclature.currency import CurrencyResponse, CurrencyCreate, CurrencyUpdate, UserCurrenciesUpdate
from service.nomenclature.currency import create_new_currency, update_currency_by_id, \
    get_currencies_by_user_id, get_all_currencies, update_currencies_by_user

router = APIRouter(tags=["Currencies"])

@router.get(
    "/currencies",
    summary="List All Currencies",
    response_model=Union[PaginatedResponse[CurrencyResponse], List[CurrencyResponse]])
async def get_currencies(db: DBSession, pagination: Pagination):
    return await get_all_currencies(db, pagination)

@router.get(
    "/users/{user_id}/currencies",
    summary="List All Available Currencies defined By User Id",
    response_model=list[CurrencyResponse])
async def get_currencies_by_user(db: DBSession, user_id: int):
    return await get_currencies_by_user_id(db, user_id)

@router.put("/users/update-currencies",
            summary='Update User Currencies',
            response_model=List[CurrencyResponse])
async def update_user_currencies(db: DBSession, currency_update: UserCurrenciesUpdate, request: Request):
    return await update_currencies_by_user(db, currency_update, request)

@router.post(
    "/currencies",
    summary="Create New Currency",
    response_model=CurrencyResponse,
    dependencies=[SuperAdminSession])
async def create_currency(db: DBSession, currency_create: CurrencyCreate):
    return await create_new_currency(db, currency_create)

@router.put(
    "/currencies/{currency_id}",
    summary="Update Currency",
    response_model=CurrencyResponse,
    dependencies=[SuperAdminSession])
async def update_currency(db: DBSession, currency_id: int, currency_update: CurrencyUpdate):
    return await update_currency_by_id(db, currency_id, currency_update)