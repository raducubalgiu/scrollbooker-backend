from typing import List

from fastapi import APIRouter
from starlette.requests import Request
from app.schema.booking.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from app.service.booking.schedule import create_user_schedule, update_user_schedule, update_user_many_schedules
from app.core.dependencies import DBSession, BusinessAndEmployeesSession

router = APIRouter(prefix="/schedules", tags=["Schedules"])

@router.post("/", response_model=ScheduleResponse, dependencies=[BusinessAndEmployeesSession])
async def create_schedule(db: DBSession, schedule_update: ScheduleCreate, request: Request):
    return await create_user_schedule(db, schedule_update, request)

@router.put("/{schedule_id}", dependencies=[BusinessAndEmployeesSession])
async def update_schedule(db: DBSession, schedule_id: int, schedule_update: ScheduleUpdate, request: Request):
    return await update_user_schedule(db, schedule_id, schedule_update, request)

@router.put("/", response_model=list[ScheduleResponse], dependencies=[BusinessAndEmployeesSession])
async def update_many_schedules(db: DBSession, schedule_update: List[ScheduleUpdate], request: Request):
    return await update_user_many_schedules(db, schedule_update, request)