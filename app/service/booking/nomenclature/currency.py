from app.core.crud_helpers import db_create, db_get_all
from app.core.dependencies import DBSession
from app.models import Currency
from app.schema.booking.nomenclature.currency import CurrencyCreate

async def get_all_currencies(db: DBSession):
    return await db_get_all(db, model=Currency)

async def create_new_currency(db: DBSession, currency_create: CurrencyCreate):
    print('CURRENCY CREATE', currency_create)
    return await db_create(db, model=Currency, create_data=currency_create)

