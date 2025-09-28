from typing import List

from fastapi import APIRouter
from starlette.requests import Request
from schema.booking.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from service.booking.schedule import create_user_schedule, update_user_schedule, update_user_schedules, \
    get_schedules_by_user_id
from core.dependencies import DBSession, BusinessAndEmployeesSession

router = APIRouter(tags=["Schedules"])

@router.get(
    "/users/{user_id}/schedules",
    summary='List All Schedules Filtered By User Id',
    response_model=list[ScheduleResponse])
async def get_user_schedules(db: DBSession, user_id: int):
    return await get_schedules_by_user_id(db, user_id)

@router.post(
    "/schedules",
    summary='Create New Schedule',
    response_model=ScheduleResponse,
    dependencies=[BusinessAndEmployeesSession])
async def create_schedule(db: DBSession, schedule_update: ScheduleCreate, request: Request):
    return await create_user_schedule(db, schedule_update, request)

@router.put(
    "/schedules/{schedule_id}",
    summary='Update One Schedule',
    dependencies=[BusinessAndEmployeesSession])
async def update_schedule(db: DBSession, schedule_id: int, schedule_update: ScheduleUpdate, request: Request):
    return await update_user_schedule(db, schedule_id, schedule_update, request)

@router.put(
    "/schedules",
    summary='Update Many Schedules',
    response_model=list[ScheduleResponse],
    dependencies=[BusinessAndEmployeesSession])
async def update_many_schedules(db: DBSession, schedule_update: List[ScheduleUpdate], request: Request):
    return await update_user_schedules(db, schedule_update, request)