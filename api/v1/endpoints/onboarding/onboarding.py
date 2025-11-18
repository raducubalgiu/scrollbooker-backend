from typing import List

from fastapi import APIRouter
from starlette.requests import Request

from core.dependencies import DBSession, BusinessSession, AuthenticatedUser
from schema.booking.business import BusinessHasEmployeesUpdate
from schema.booking.schedule import ScheduleUpdate
from schema.nomenclature.currency import UserCurrenciesUpdate
from schema.nomenclature.service import ServiceIdsUpdate
from schema.onboarding.onboarding import OnBoardingResponse
from schema.user.user import UsernameUpdate, BirthDateUpdate, GenderUpdate
from service.onboarding.collect_business import collect_business_services, collect_business_schedules, \
    collect_business_has_employees, collect_business_currencies
from service.onboarding.collect_client import collect_client_birthdate, collect_client_gender
from service.onboarding.collect_shared import collect_user_username, collect_user_location_permission

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

# Shared
@router.patch("/collect-user-username",
              summary='Collect User Username',
              response_model=OnBoardingResponse)
async def collect_username(
    db: DBSession,
    username_update: UsernameUpdate,
    auth_user: AuthenticatedUser
) -> OnBoardingResponse:
    return await collect_user_username(db, username_update, auth_user)

# Client
@router.patch("/collect-client-birthdate",
              summary='Collect User Birthdate as Client',
              response_model=OnBoardingResponse)
async def collect_birthdate(
    db: DBSession,
    birthdate_update: BirthDateUpdate,
    auth_user: AuthenticatedUser
) -> OnBoardingResponse:
    return await collect_client_birthdate(db, birthdate_update, auth_user)

@router.patch("/collect-client-gender",
              summary='Collect User Gender as Client',
              response_model=OnBoardingResponse)
async def collect_gender(
    db: DBSession,
    gender_update: GenderUpdate,
    auth_user: AuthenticatedUser
) -> OnBoardingResponse:
    return await collect_client_gender(db, gender_update, auth_user)

@router.patch("/collect-user-location-permission",
              summary='Collect User Location Permission',
              response_model=OnBoardingResponse)
async def collect_location_permission(db: DBSession, auth_user: AuthenticatedUser) -> OnBoardingResponse:
    return await collect_user_location_permission(db, auth_user)

# Business
# Collect Business (Create Business)

# Collect Business Services
@router.patch("/collect-business-services",
              summary='Collect Business Services',
              response_model=OnBoardingResponse,
              dependencies=[BusinessSession])
async def collect_services(
        db: DBSession,
        services_update: ServiceIdsUpdate,
        auth_user: AuthenticatedUser
) -> OnBoardingResponse:
    return await collect_business_services(db, services_update, auth_user)

# Collect Business Schedules
@router.patch(
    "/collect-business-schedules",
    summary='Collect Business Schedules',
    response_model=OnBoardingResponse,
    dependencies=[BusinessSession])
async def collect_schedules(
        db: DBSession,
        schedule_update: List[ScheduleUpdate],
        auth_user: AuthenticatedUser
) -> OnBoardingResponse:
    return await collect_business_schedules(db, schedule_update, auth_user)

# Collect Business Has Employees
@router.patch("/collect-business-has-employees",
              summary='Collect Business Has Employees',
              response_model=OnBoardingResponse,
              dependencies=[BusinessSession])
async def collect_has_employees(
        db: DBSession,
        business_update: BusinessHasEmployeesUpdate,
        auth_user: AuthenticatedUser
) -> OnBoardingResponse:
    return await collect_business_has_employees(db, business_update, auth_user)

# Collect Business Has Employees
@router.patch("/collect-business-currencies",
            summary='CollectBusinessCurrencies',
            response_model=OnBoardingResponse)
async def collect_currencies(
        db: DBSession,
        currency_update: UserCurrenciesUpdate,
        auth_user: AuthenticatedUser
) -> OnBoardingResponse:
    return await collect_business_currencies(db, currency_update, auth_user)

# Collect Business Validation