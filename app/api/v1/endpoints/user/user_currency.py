from fastapi import APIRouter
from starlette.requests import Request
from starlette import status
from app.core.dependencies import BusinessAndEmployeesSession, DBSession
from app.schema.user.user_currency import UserCurrencyResponse, UserCurrencyCreate, UserCurrencyUpdate
from app.service.user.user_currency import create_new_user_currency, delete_new_user_currency

router = APIRouter(prefix="/user-currencies", tags=["User Currencies"])

@router.post("/", response_model=UserCurrencyResponse, dependencies=[BusinessAndEmployeesSession])
async def create_user_currency(db: DBSession, user_currency_create: UserCurrencyCreate, request: Request):
    return await create_new_user_currency(db, user_currency_create, request)

@router.put("/", status_code=status.HTTP_204_NO_CONTENT, dependencies=[BusinessAndEmployeesSession])
async def delete_user_currency(db: DBSession, user_currency_update: UserCurrencyUpdate, request: Request):
    return await delete_new_user_currency(db, user_currency_update, request)
