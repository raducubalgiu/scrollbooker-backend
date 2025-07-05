from typing import List

from fastapi import HTTPException
from starlette.requests import Request
from starlette import status
from sqlalchemy import select, or_
from core.crud_helpers import db_get_one, db_get_all
from core.dependencies import DBSession, check_resource_ownership
from core.enums.registration_step_enum import RegistrationStepEnum
from schema.booking.schedule import ScheduleCreate, ScheduleUpdate
from models import Schedule, Business, User
import calendar
from core.logger import logger
from schema.user.user import UserAuthStateResponse

from service.booking.business import get_business_by_user_id

async def get_business(db: DBSession, auth_user_id: int):
    business_stmt = await db.execute(
        select(Business)
        .join(User, User.id == auth_user_id) #type: ignore
        .where(or_(
            Business.owner_id == auth_user_id,
            User.employee_business_id == Business.id
        ))
    )

    business = business_stmt.scalar_one_or_none()

    if not business:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='You do not have permissions to perform this action')

    return business

async def get_schedules_by_user_id(db: DBSession, user_id: int):
    await get_business_by_user_id(db, user_id)
    schedules = await db_get_all(db, model=Schedule, filters={Schedule.user_id: user_id}, order_by="day_week_index")

    return schedules

async def create_user_schedule(db: DBSession, schedule_create: ScheduleCreate, request: Request):
    auth_user_id = request.state.user.get("id")
    business = await get_business(db, auth_user_id)

    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Business not found')

    existing_schedule = await db_get_one(db, model=Schedule, raise_not_found=False,
                            filters={
                                Schedule.user_id: auth_user_id,
                                Schedule.day_of_week: schedule_create.day_of_week})

    if existing_schedule:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Schedule is already defined')

    day_week_index = list(calendar.day_name).index(schedule_create.day_of_week)

    new_schedule = Schedule(
        user_id=auth_user_id,
        business_id=business.id,
        day_of_week=schedule_create.day_of_week,
        start_time=schedule_create.start_time,
        end_time=schedule_create.end_time,
        day_week_index=day_week_index
    )


    db.add(new_schedule)
    await db.commit()
    await db.refresh(new_schedule)
    return new_schedule

async def update_user_schedule(db: DBSession, schedule_id: int, schedule_update: ScheduleUpdate, request: Request):
    auth_user_id = request.state.user.get("id")
    schedule = await check_resource_ownership(db, Schedule, schedule_id, request)
    await get_business(db, auth_user_id)

    schedule.start_time = schedule_update.start_time
    schedule.end_time = schedule_update.end_time

    await db.commit()
    await db.refresh(schedule)

    return schedule

async def update_user_many_schedules(db: DBSession, schedule_update: List[ScheduleUpdate], request: Request):
    auth_user_id = request.state.user.get("id")

    try:
        updated_schedules = []

        for schedule in schedule_update:
            updated_schedule = await update_user_schedule(db, schedule.id, schedule, request)
            updated_schedules.append(updated_schedule)

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

    except Exception as e:
        await db.rollback()

        logger.error(f"Schedules could not be updated. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )