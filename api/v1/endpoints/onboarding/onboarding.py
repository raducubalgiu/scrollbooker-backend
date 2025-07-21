from fastapi import APIRouter
from starlette.requests import Request

from core.dependencies import DBSession
from schema.onboarding.onboarding import OnBoardingResponse
from schema.user.user import UsernameUpdate, BirthDateUpdate, GenderUpdate
from service.onboarding.collect_client import collect_client_birthdate, collect_client_gender
from service.onboarding.collect_shared import collect_user_username

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

@router.patch("/collect-user-username",
              summary='Collect User Username',
              response_model=OnBoardingResponse)
async def collect_username(db: DBSession, username_update: UsernameUpdate, request: Request):
    return await collect_user_username(db, username_update, request)

@router.patch("/collect-client-birthdate",
              summary='Collect User Birthdate as Client',
              response_model=OnBoardingResponse)
async def collect_birthdate(db: DBSession, birthdate_update: BirthDateUpdate, request: Request):
    return await collect_client_birthdate(db, birthdate_update, request)

@router.patch("/collect-client-gender",
              summary='Collect User Gender as Client',
              response_model=OnBoardingResponse)
async def collect_gender(db: DBSession, gender_update: GenderUpdate, request: Request):
    return await collect_client_gender(db, gender_update, request)