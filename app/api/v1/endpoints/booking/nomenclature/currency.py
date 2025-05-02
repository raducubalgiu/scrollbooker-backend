from typing import Union

from fastapi import APIRouter

from app.core.crud_helpers import PaginatedResponse
from app.core.dependencies import DBSession, SuperAdminSession, Pagination
from app.schema.booking.nomenclature.currency import CurrencyResponse, CurrencyCreate, CurrencyUpdate
from app.service.booking.nomenclature.currency import get_all_currencies, create_new_currency, update_currency_by_id

router = APIRouter(prefix="/currencies", tags=["Currencies"])

@router.get("/", response_model=Union[PaginatedResponse[CurrencyResponse], list[CurrencyResponse]])
async def get_currencies(db: DBSession, pagination: Pagination):
    return await get_all_currencies(db, pagination)

@router.post("/", response_model=CurrencyResponse, dependencies=[SuperAdminSession])
async def create_currency(db: DBSession, currency_create: CurrencyCreate):
    return await create_new_currency(db, currency_create)

@router.put("/{currency_id}", response_model=CurrencyResponse, dependencies=[SuperAdminSession])
async def update_currency(db: DBSession, currency_id: int, currency_update: CurrencyUpdate):
    return await update_currency_by_id(db, currency_id, currency_update)