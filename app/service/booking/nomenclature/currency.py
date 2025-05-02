from app.core.crud_helpers import db_create, db_get_all, db_update
from app.core.dependencies import DBSession, Pagination
from app.models import Currency
from app.schema.booking.nomenclature.currency import CurrencyCreate, CurrencyResponse, CurrencyUpdate

async def get_all_currencies(db: DBSession, pagination: Pagination):
    return await db_get_all(db, model=Currency, schema=CurrencyResponse, page=pagination.page, limit=pagination.limit, order_by="created_at", descending=True)

async def create_new_currency(db: DBSession, currency_create: CurrencyCreate):
    return await db_create(db, model=Currency, create_data=currency_create)

async def update_currency_by_id(db: DBSession, currency_id: int, currency_update: CurrencyUpdate):
    return await db_update(db, model=Currency, resource_id=currency_id, update_data=currency_update)
