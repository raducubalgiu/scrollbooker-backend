from typing import List

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette import status
from core.dependencies import DBSession
from core.enums.registration_step_enum import RegistrationStepEnum
from models import User
from schema.booking.business import BusinessHasEmployeesUpdate
from schema.booking.schedule import ScheduleUpdate
from schema.nomenclature.service import ServiceIdsUpdate
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
async def collect_business_has_employees(db: DBSession, business_update: BusinessHasEmployeesUpdate, request: Request):
    business = await update_business_has_employees(db, business_update, request)

    if not business:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )

    owner = await db.get(User, business.owner_id)

    if owner.registration_step is RegistrationStepEnum.COLLECT_BUSINESS_HAS_EMPLOYEES:
        owner.registration_step = RegistrationStepEnum.COLLECT_BUSINESS_VALIDATION

    db.add(owner)

    await db.commit()
    await db.refresh(owner)

    return UserAuthStateResponse(
        is_validated=owner.is_validated,
        registration_step=owner.registration_step
    )

# Collect Business Validation