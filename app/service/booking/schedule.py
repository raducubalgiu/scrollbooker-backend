from fastapi import HTTPException
from starlette.requests import Request
from starlette import status
from app.core.crud_helpers import db_get_one
from app.core.data_utils import local_to_utc
from app.core.dependencies import DBSession, check_resource_ownership
from app.schema.booking.schedule import ScheduleCreate, ScheduleUpdate
from app.models import Schedule, Business, User

async def get_start_end_time(timezone, schedule: ScheduleCreate | ScheduleUpdate):
    if schedule.start_time and schedule.end_time:
        # Apply UTC timezone
        start_time_utc = await local_to_utc(timezone=timezone, local_time=schedule.start_time)
        end_time_utc = await local_to_utc(timezone=timezone, local_time=schedule.end_time)

        return { "start_time": start_time_utc.timetz(), "end_time": end_time_utc.timetz() }
    else:
        return { "start_time": None, "end_time": None }

async def create_user_schedule(db: DBSession, business_id: int, schedule_create: ScheduleCreate, request: Request):
    auth_user_id = request.state.user.get("id")
    business = await db_get_one(db, model=Business, filters={Business.id: business_id})

    existing_schedule = await db_get_one(db, model=Schedule,
        filters={Schedule.user_id: auth_user_id, Schedule.day_of_week: schedule_create.day_of_week}, raise_not_found=False)

    is_employee_of_business = await db_get_one(db, model=User,
        filters={User.business_employee_id: business_id}, raise_not_found=False)

    is_business_owner = business.owner_id == auth_user_id

    if existing_schedule:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Schedule is already defined')

    start_end_time = await get_start_end_time(business.timezone, schedule_create)

    if is_business_owner or is_employee_of_business:
        new_schedule = Schedule(
            user_id=auth_user_id,
            business_id=business_id,
            day_of_week=schedule_create.day_of_week,
            start_time=start_end_time["start_time"],
            end_time=start_end_time["end_time"]
        )

        db.add(new_schedule)
        await db.commit()
        await db.refresh(new_schedule)
        return new_schedule
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You do not have permission to perform this action')

async def update_user_schedule(db: DBSession, business_id: int, schedule_id: int, schedule_update: ScheduleUpdate, request: Request):
    schedule = await check_resource_ownership(db, Schedule, schedule_id, request)
    business = await db_get_one(db, model=Business, filters={Business.id: business_id})

    start_end_time = await get_start_end_time(business.timezone, schedule_update)

    schedule.start_time = start_end_time["start_time"]
    schedule.end_time = start_end_time["end_time"]

    await db.commit()
    await db.refresh(schedule)

    return schedule
