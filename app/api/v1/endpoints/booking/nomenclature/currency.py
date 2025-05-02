from fastapi import APIRouter

from app.core.dependencies import DBSession, SuperAdminSession
from app.schema.booking.nomenclature.currency import CurrencyResponse, CurrencyCreate
from app.service.booking.nomenclature.currency import get_all_currencies, create_new_currency

router = APIRouter(prefix="/currencies", tags=["Currencies"])

@router.get("/", response_model=list[CurrencyResponse])
async def get_currencies(db: DBSession):
    return await get_all_currencies(db)

@router.post("/", response_model=CurrencyResponse, dependencies=[SuperAdminSession])
async def create_currency(db: DBSession, currency_create: CurrencyCreate):
    return await create_new_currency(db, currency_create)