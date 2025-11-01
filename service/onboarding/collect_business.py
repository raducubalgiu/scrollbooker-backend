from typing import List

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette import status

from api.v1.endpoints.nomenclature.currency import update_user_currencies
from core.dependencies import DBSession
from core.logger import logger
from core.enums.registration_step_enum import RegistrationStepEnum
from models import User
from schema.booking.business import BusinessHasEmployeesUpdate
from schema.booking.schedule import ScheduleUpdate
from schema.nomenclature.currency import UserCurrenciesUpdate
from schema.nomenclature.service import ServiceIdsUpdate
from schema.onboarding.onboarding import OnBoardingResponse
from schema.user.user import UserAuthStateResponse
from service.booking.business import update_business_has_employees
from service.booking.schedule import update_user_schedules
from service.nomenclature.service import update_services_by_business_id

# Collect Business (create Business)

# Collect Business Services
async def collect_business_services(db: DBSession, services_update: ServiceIdsUpdate, request: Request):
    auth_user_id = request.state.user.get("id")
    services = await update_services_by_business_id(db, services_update, request)

    if not services:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )

    user = await db.get(User, auth_user_id)

    if user.registration_step is RegistrationStepEnum.COLLECT_BUSINESS_SERVICES:
        user.registration_step = RegistrationStepEnum.COLLECT_BUSINESS_SCHEDULES

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return UserAuthStateResponse(
        is_validated=user.is_validated,
        registration_step=user.registration_step
    )

# Collect Business Schedules
async def collect_business_schedules(db: DBSession, schedule_update: List[ScheduleUpdate], request: Request):
    auth_user_id = request.state.user.get("id")
    schedules = await update_user_schedules(db, schedule_update, request)

    if not schedules:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )

    user = await db.get(User, auth_user_id)

    if user.registration_step is RegistrationStepEnum.COLLECT_BUSINESS_SCHEDULES:
        user.registration_step = RegistrationStepEnum.COLLECT_BUSINESS_HAS_EMPLOYEES

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserAuthStateResponse(
        is_validated=user.is_validated,
        registration_step=user.registration_step
    )

# Collect Business Has Employees
async def collect_business_has_employees(
        db: DBSession,
        business_update: BusinessHasEmployeesUpdate,
        request: Request
) -> OnBoardingResponse:
    business = await update_business_has_employees(db, business_update, request)

    if not business:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )

    owner = await db.get(User, business.owner_id)

    if business.has_employees and owner.registration_step is RegistrationStepEnum.COLLECT_BUSINESS_HAS_EMPLOYEES:
        owner.registration_step = RegistrationStepEnum.COLLECT_BUSINESS_VALIDATION
    elif owner.registration_step is RegistrationStepEnum.COLLECT_BUSINESS_HAS_EMPLOYEES:
        owner.registration_step = RegistrationStepEnum.COLLECT_BUSINESS_CURRENCIES

    db.add(owner)

    await db.commit()
    await db.refresh(owner)

    return OnBoardingResponse(
        is_validated=owner.is_validated,
        registration_step=owner.registration_step
    )

# Collect Business Currencies
async def collect_business_currencies(
        db: DBSession,
        currency_update: UserCurrenciesUpdate,
        request: Request
) -> OnBoardingResponse:
    auth_user_id = request.state.user.get("id")

    updated_user_currencies = await update_user_currencies(db, currency_update, request)

    if not updated_user_currencies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )

    user = await db.get(User, auth_user_id)

    if user.registration_step is RegistrationStepEnum.COLLECT_BUSINESS_CURRENCIES:
        user.registration_step = RegistrationStepEnum.COLLECT_BUSINESS_VALIDATION

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return OnBoardingResponse(
        is_validated=user.is_validated,
        registration_step=user.registration_step
    )

# Collect Business Validation